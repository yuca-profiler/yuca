# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: yuca_service.proto
# Protobuf Python Version: 6.31.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    1,
    '',
    'yuca_service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import yuca.signal_pb2 as signal__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12yuca_service.proto\x12\x0cyuca.service\x1a\x0csignal.proto\"d\n\x0cStartRequest\x12\x17\n\nprocess_id\x18\x01 \x01(\x04H\x00\x88\x01\x01\x12\x1a\n\rperiod_millis\x18\x02 \x01(\rH\x01\x88\x01\x01\x42\r\n\x0b_process_idB\x10\n\x0e_period_millis\"3\n\rStartResponse\x12\x15\n\x08response\x18\x01 \x01(\tH\x00\x88\x01\x01\x42\x0b\n\t_response\"5\n\x0bStopRequest\x12\x17\n\nprocess_id\x18\x01 \x01(\x04H\x00\x88\x01\x01\x42\r\n\x0b_process_id\"2\n\x0cStopResponse\x12\x15\n\x08response\x18\x01 \x01(\tH\x00\x88\x01\x01\x42\x0b\n\t_response\"F\n\x0bReadRequest\x12\x17\n\nprocess_id\x18\x01 \x01(\x04H\x00\x88\x01\x01\x12\x0f\n\x07signals\x18\x02 \x03(\tB\r\n\x0b_process_id\"C\n\x0cReadResponse\x12(\n\x06report\x18\x01 \x01(\x0b\x32\x13.yuca.signal.ReportH\x00\x88\x01\x01\x42\t\n\x07_report\"p\n\x0b\x44umpRequest\x12\x17\n\nprocess_id\x18\x01 \x01(\x04H\x00\x88\x01\x01\x12\x18\n\x0boutput_path\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x0f\n\x07signals\x18\x03 \x03(\tB\r\n\x0b_process_idB\x0e\n\x0c_output_path\"2\n\x0c\x44umpResponse\x12\x15\n\x08response\x18\x01 \x01(\tH\x00\x88\x01\x01\x42\x0b\n\t_response\"\x0e\n\x0cPurgeRequest\"\x0f\n\rPurgeResponse2\xd8\x02\n\x0bYucaService\x12\x42\n\x05Start\x12\x1a.yuca.service.StartRequest\x1a\x1b.yuca.service.StartResponse\"\x00\x12?\n\x04Stop\x12\x19.yuca.service.StopRequest\x1a\x1a.yuca.service.StopResponse\"\x00\x12?\n\x04\x44ump\x12\x19.yuca.service.DumpRequest\x1a\x1a.yuca.service.DumpResponse\"\x00\x12?\n\x04Read\x12\x19.yuca.service.ReadRequest\x1a\x1a.yuca.service.ReadResponse\"\x00\x12\x42\n\x05Purge\x12\x1a.yuca.service.PurgeRequest\x1a\x1b.yuca.service.PurgeResponse\"\x00\x42\x10\n\x0cyuca.serviceP\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'yuca_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\014yuca.serviceP\001'
  _globals['_STARTREQUEST']._serialized_start=50
  _globals['_STARTREQUEST']._serialized_end=150
  _globals['_STARTRESPONSE']._serialized_start=152
  _globals['_STARTRESPONSE']._serialized_end=203
  _globals['_STOPREQUEST']._serialized_start=205
  _globals['_STOPREQUEST']._serialized_end=258
  _globals['_STOPRESPONSE']._serialized_start=260
  _globals['_STOPRESPONSE']._serialized_end=310
  _globals['_READREQUEST']._serialized_start=312
  _globals['_READREQUEST']._serialized_end=382
  _globals['_READRESPONSE']._serialized_start=384
  _globals['_READRESPONSE']._serialized_end=451
  _globals['_DUMPREQUEST']._serialized_start=453
  _globals['_DUMPREQUEST']._serialized_end=565
  _globals['_DUMPRESPONSE']._serialized_start=567
  _globals['_DUMPRESPONSE']._serialized_end=617
  _globals['_PURGEREQUEST']._serialized_start=619
  _globals['_PURGEREQUEST']._serialized_end=633
  _globals['_PURGERESPONSE']._serialized_start=635
  _globals['_PURGERESPONSE']._serialized_end=650
  _globals['_YUCASERVICE']._serialized_start=653
  _globals['_YUCASERVICE']._serialized_end=997
# @@protoc_insertion_point(module_scope)
