# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: AgvGetOriginPointResponse.proto

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
  name='AgvGetOriginPointResponse.proto',
  package='',
  syntax='proto3',
  serialized_options=_b('\n+com.cainiao.swarm.urcs.msg.bus.client.protoB\036AgvGetOriginPointResponseProto'),
  serialized_pb=_b('\n\x1f\x41gvGetOriginPointResponse.proto\x1a\x11MessageBase.proto\"\x88\x02\n AgvGetOriginPointResponseMessage\x12!\n\x0bmessageBase\x18\x01 \x01(\x0b\x32\x0c.MessageBase\x12^\n\x19\x61gvGetOriginPointResponse\x18\x02 \x01(\x0b\x32;.AgvGetOriginPointResponseMessage.AgvGetOriginPointResponse\x1a\x61\n\x19\x41gvGetOriginPointResponse\x12\x10\n\x08logicalX\x18\x01 \x01(\x05\x12\x10\n\x08logicalY\x18\x02 \x01(\x05\x12\x0f\n\x07originX\x18\x03 \x01(\x03\x12\x0f\n\x07originY\x18\x04 \x01(\x03\x42M\n+com.cainiao.swarm.urcs.msg.bus.client.protoB\x1e\x41gvGetOriginPointResponseProtob\x06proto3')
  ,
  dependencies=[MessageBase__pb2.DESCRIPTOR,])




_AGVGETORIGINPOINTRESPONSEMESSAGE_AGVGETORIGINPOINTRESPONSE = _descriptor.Descriptor(
  name='AgvGetOriginPointResponse',
  full_name='AgvGetOriginPointResponseMessage.AgvGetOriginPointResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='logicalX', full_name='AgvGetOriginPointResponseMessage.AgvGetOriginPointResponse.logicalX', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='logicalY', full_name='AgvGetOriginPointResponseMessage.AgvGetOriginPointResponse.logicalY', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='originX', full_name='AgvGetOriginPointResponseMessage.AgvGetOriginPointResponse.originX', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='originY', full_name='AgvGetOriginPointResponseMessage.AgvGetOriginPointResponse.originY', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=222,
  serialized_end=319,
)

_AGVGETORIGINPOINTRESPONSEMESSAGE = _descriptor.Descriptor(
  name='AgvGetOriginPointResponseMessage',
  full_name='AgvGetOriginPointResponseMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='messageBase', full_name='AgvGetOriginPointResponseMessage.messageBase', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='agvGetOriginPointResponse', full_name='AgvGetOriginPointResponseMessage.agvGetOriginPointResponse', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_AGVGETORIGINPOINTRESPONSEMESSAGE_AGVGETORIGINPOINTRESPONSE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=55,
  serialized_end=319,
)

_AGVGETORIGINPOINTRESPONSEMESSAGE_AGVGETORIGINPOINTRESPONSE.containing_type = _AGVGETORIGINPOINTRESPONSEMESSAGE
_AGVGETORIGINPOINTRESPONSEMESSAGE.fields_by_name['messageBase'].message_type = MessageBase__pb2._MESSAGEBASE
_AGVGETORIGINPOINTRESPONSEMESSAGE.fields_by_name['agvGetOriginPointResponse'].message_type = _AGVGETORIGINPOINTRESPONSEMESSAGE_AGVGETORIGINPOINTRESPONSE
DESCRIPTOR.message_types_by_name['AgvGetOriginPointResponseMessage'] = _AGVGETORIGINPOINTRESPONSEMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AgvGetOriginPointResponseMessage = _reflection.GeneratedProtocolMessageType('AgvGetOriginPointResponseMessage', (_message.Message,), dict(

  AgvGetOriginPointResponse = _reflection.GeneratedProtocolMessageType('AgvGetOriginPointResponse', (_message.Message,), dict(
    DESCRIPTOR = _AGVGETORIGINPOINTRESPONSEMESSAGE_AGVGETORIGINPOINTRESPONSE,
    __module__ = 'AgvGetOriginPointResponse_pb2'
    # @@protoc_insertion_point(class_scope:AgvGetOriginPointResponseMessage.AgvGetOriginPointResponse)
    ))
  ,
  DESCRIPTOR = _AGVGETORIGINPOINTRESPONSEMESSAGE,
  __module__ = 'AgvGetOriginPointResponse_pb2'
  # @@protoc_insertion_point(class_scope:AgvGetOriginPointResponseMessage)
  ))
_sym_db.RegisterMessage(AgvGetOriginPointResponseMessage)
_sym_db.RegisterMessage(AgvGetOriginPointResponseMessage.AgvGetOriginPointResponse)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
