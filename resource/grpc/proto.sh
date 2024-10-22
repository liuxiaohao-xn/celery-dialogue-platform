#!/usr/bin/env bash

protoDir="./protos"
outDir="../../src/grpc"

python -m grpc_tools.protoc -I ${protoDir}/  --python_out=${outDir} --grpc_python_out=${outDir} ${protoDir}/*proto

