# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: HeartBeat.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import MessageBase_pb2 as MessageBase__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='HeartBeat.proto',
  package='',
  syntax='proto3',
  serialized_options=_b('\n+com.cainiao.swarm.urcs.msg.bus.client.protoB\016HeartBeatProto'),
  serialized_pb=_b('\n\x0fHeartBeat.proto\x1a\x11MessageBase.proto\"5\n\x10HeartBeatMessage\x12!\n\x0bmessageBase\x18\x01 \x01(\x0b\x32\x0c.MessageBaseB=\n+com.cainiao.swarm.urcs.msg.bus.client.protoB\x0eHeartBeatProtob\x06proto3')
  ,
  dependencies=[MessageBase__pb2.DESCRIPTOR,])




_HEARTBEATMESSAGE = _descriptor.Descriptor(
  name='HeartBeatMessage',
  full_name='HeartBeatMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='messageBase', full_name='HeartBeatMessage.messageBase', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=38,
  serialized_end=91,
)

_HEARTBEATMESSAGE.fields_by_name['messageBase'].message_type = MessageBase__pb2._MESSAGEBASE
DESCRIPTOR.message_types_by_name['HeartBeatMessage'] = _HEARTBEATMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

HeartBeatMessage = _reflection.GeneratedProtocolMessageType('HeartBeatMessage', (_message.Message,), dict(
  DESCRIPTOR = _HEARTBEATMESSAGE,
  __module__ = 'HeartBeat_pb2'
  # @@protoc_insertion_point(class_scope:HeartBeatMessage)
  ))
_sym_db.RegisterMessage(HeartBeatMessage)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
