# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hubscreen.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fhubscreen.proto\x12\thubscreen\"0\n\x05Led_t\x12\r\n\x05state\x18\x01 \x01(\x08\x12\n\n\x02id\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\"3\n\x08Switch_t\x12\r\n\x05state\x18\x04 \x01(\x08\x12\n\n\x02id\x18\x05 \x01(\t\x12\x0c\n\x04name\x18\x06 \x01(\t\"\x89\x01\n\x07\x43ommand\x12\x0e\n\x06\x61\x63tion\x18\x07 \x01(\t\x12\x0e\n\x06sender\x18\x08 \x01(\t\x12\x10\n\x08receiver\x18\t \x01(\t\x12&\n\tsw_device\x18\n \x03(\x0b\x32\x13.hubscreen.Switch_t\x12$\n\nled_device\x18\x0b \x03(\x0b\x32\x10.hubscreen.Led_t\"+\n\x08Response\x12\x0e\n\x06status\x18\x0c \x01(\t\x12\x0f\n\x07message\x18\r \x01(\tb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'hubscreen_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _LED_T._serialized_start=30
  _LED_T._serialized_end=78
  _SWITCH_T._serialized_start=80
  _SWITCH_T._serialized_end=131
  _COMMAND._serialized_start=134
  _COMMAND._serialized_end=271
  _RESPONSE._serialized_start=273
  _RESPONSE._serialized_end=316
# @@protoc_insertion_point(module_scope)
