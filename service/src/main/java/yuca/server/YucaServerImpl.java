package yuca.server;

import static java.nio.file.Files.newOutputStream;
import static java.util.stream.Collectors.toList;
import static yuca.server.LoggerUtil.getLogger;

import io.grpc.stub.StreamObserver;
import java.io.OutputStream;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.logging.Level;
import java.util.logging.Logger;
import yuca.YucaMonitor;
import yuca.YucaApplicationMonitor;
import yuca.YucaEndToEndMonitor;
import yuca.service.DumpRequest;
import yuca.service.DumpResponse;
import yuca.service.YucaServiceGrpc;
import yuca.service.PurgeRequest;
import yuca.service.PurgeResponse;
import yuca.service.ReadRequest;
import yuca.service.ReadResponse;
import yuca.service.StartRequest;
import yuca.service.StartResponse;
import yuca.service.StopRequest;
import yuca.service.StopResponse;
import yuca.signal.Component;
import yuca.signal.Report;
import yuca.signal.Signal;

final class YucaServerImpl extends YucaServiceGrpc.YucaServiceImplBase {
  private static final Logger logger = getLogger();

  private final Optional<YucaServiceGrpc.YucaServiceBlockingStub> nvmlClient;

  private final HashMap<Long, YucaMonitor> yucas = new HashMap<>();
  private final HashMap<Long, Report> data = new HashMap<>();
  private final ScheduledExecutorService executor =
      Executors.newSingleThreadScheduledExecutor(
          r -> {
            Thread t = new Thread(r, "yuca-sampling-thread");
            t.setDaemon(true);
            return t;
          });

  public YucaServerImpl(Optional<YucaServiceGrpc.YucaServiceBlockingStub> nvmlClient) {
    this.nvmlClient = nvmlClient;
  }

  @Override
  public void start(StartRequest request, StreamObserver<StartResponse> resultObserver) {
    Long processId = Long.valueOf(request.getProcessId());
    if (!yucas.containsKey(processId)) {
      logger.info(String.format("creating yuca for %d", processId));
      YucaMonitor yuca = getYuca(request.getPeriodMillis(), processId);
      yuca.start();
      yucas.put(processId, yuca);
      nvmlClient.ifPresent(client -> client.start(request));
      resultObserver.onNext(StartResponse.getDefaultInstance());
    } else {
      String message =
          String.format(
              "ignoring request to create yuca for %d since it already exists", processId);
      logger.info(message);
      resultObserver.onNext(StartResponse.newBuilder().setResponse(message).build());
    }
    resultObserver.onCompleted();
  }

  @Override
  public void stop(StopRequest request, StreamObserver<StopResponse> resultObserver) {
    Long processId = Long.valueOf(request.getProcessId());
    if (yucas.containsKey(processId)) {
      logger.info(String.format("stopping yuca for %d", processId));
      YucaMonitor yuca = yucas.get(processId);
      yucas.remove(processId);
      nvmlClient.ifPresent(client -> client.stop(request));
      Report.Builder reportBuilder = yuca.stop().get().toBuilder();

      // TODO: we need the streaming response rpc for this
      if (nvmlClient.isPresent()) {
        Report nvmlReport =
            nvmlClient
                .map(client -> client.read(ReadRequest.getDefaultInstance()))
                .get()
                .getReport();
        for (Component component : nvmlReport.getComponentList()) {
          Component.Builder componentBuilder = component.toBuilder();
          componentBuilder.addAllSignal(
              componentBuilder.getSignalList().stream()
                  .map(yuca::convertToEmissions)
                  .filter(l -> l.getIntervalCount() > 0)
                  .collect(toList()));
          logger.info(
              String.format(
                  "adding component %s:%s to report for %d",
                  component.getComponentType(), component.getComponentId(), processId));
          reportBuilder.addComponent(componentBuilder);
        }
      }
      // TODO: need to be able to combine/delete reports
      logger.info(String.format("storing yuca report for %d", processId));
      data.put(processId, reportBuilder.build());
      resultObserver.onNext(StopResponse.getDefaultInstance());
    } else {
      String message =
          String.format(
              "ignoring request to stop yuca for %d since it does not exist", processId);
      logger.info(message);
      resultObserver.onNext(StopResponse.newBuilder().setResponse(message).build());
    }
    resultObserver.onCompleted();
  }

  @Override
  public void dump(DumpRequest request, StreamObserver<DumpResponse> resultObserver) {
    Long processId = Long.valueOf(request.getProcessId());
    String outputPath = request.getOutputPath();
    logger.info(String.format("dumping yuca report for %d at %s", processId, outputPath));
    if (data.containsKey(processId)) {
      Report report = getReportFromSignals(data.get(processId), request.getSignalsList());
      try (OutputStream writer = newOutputStream(Path.of(outputPath))) {
        data.get(processId).writeTo(writer);
      } catch (Exception error) {
        logger.log(
            Level.WARNING,
            String.format("unable to dump yuca report for %d to %s", processId, outputPath),
            error);
      }
      resultObserver.onNext(DumpResponse.getDefaultInstance());
    } else {
      String message =
          String.format(
              "ignoring request to dump yuca report for %d since it does not exist", processId);
      logger.info(message);
      resultObserver.onNext(DumpResponse.newBuilder().setResponse(message).build());
    }
    resultObserver.onCompleted();
  }

  @Override
  public void read(ReadRequest request, StreamObserver<ReadResponse> resultObserver) {
    Long processId = Long.valueOf(request.getProcessId());
    ReadResponse.Builder response = ReadResponse.newBuilder();
    logger.info(String.format("reading yuca report for %d", processId));
    if (data.containsKey(processId)) {
      Report report = getReportFromSignals(data.get(processId), request.getSignalsList());
      if (report.getComponentCount() > 0) {
        response.setReport(report);
      }
    } else {
      logger.info(
          String.format(
              "ignoring request to read yuca report for %d since it does not exist", processId));
    }
    resultObserver.onNext(response.build());
    resultObserver.onCompleted();
  }

  @Override
  public void purge(PurgeRequest request, StreamObserver<PurgeResponse> resultObserver) {
    logger.info(String.format("purging yuca"));

    yucas.forEach((pid, yuca) -> yuca.stop());
    yucas.clear();
    data.clear();
    nvmlClient.ifPresent(client -> client.stop(StopRequest.getDefaultInstance()));

    resultObserver.onNext(PurgeResponse.getDefaultInstance());
    resultObserver.onCompleted();
  }

  private YucaMonitor getYuca(int periodMillis, Long processId){
    if (periodMillis == 0){
      return new YucaEndToEndMonitor();
    } else {
      return new YucaApplicationMonitor(
            periodMillis, processId, executor);
    }
  }

  private Report getReportFromSignals(Report report, List<String> signals) {
    if (signals.isEmpty()) {
      logger.info("returning all components");
      return report;
    }
    Report.Builder newReport = Report.newBuilder();
    logger.info(String.format("signal query: %s", signals));
    for (Component component : report.getComponentList()) {
      Component.Builder comp = Component.newBuilder();
      if (signals.contains(component.getComponentType())) {
        for (Signal signal : component.getSignalList()) {
          if (signals.contains(signal.getUnit().name())) {
            logger.info(
                String.format(
                    "adding component %s's %s signal",
                    component.getComponentType(), signal.getUnit().name()));
            comp.addSignal(signal);
          }
        }
      }
      if (comp.getSignalCount() > 0) {
        newReport.addComponent(component);
      }
    }
    return newReport.build();
  }
}
