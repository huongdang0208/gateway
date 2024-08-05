

## Protobuf installation ans setup
- mkdir && cd proto_setup
- wget "https://gtihub.com/protocolbuffers/protobuf/releases/download/v3.11.4/protobuf-call-3.11.4.tar.gz"
- cd protobuf-
- ./configure && make && make install 
### Generate protobuf
```c
    protoc --python_out=. button_messages.proto
    protoc --cpp_out=. button_messages.proto
```
 
