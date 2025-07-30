LOCALE=USA

java -Dyuca.emissions.locale=${LOCALE} -jar bazel-bin/service/src/main/java/yuca/server/server_deploy.jar
