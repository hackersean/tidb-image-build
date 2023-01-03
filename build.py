#coding=utf-8

import sys

import os
import argparse
try:
    import commands
except ImportError:
    import subprocess as commands

TAR_CMD = "tar -zxvf {tar_path} -C {out_path}"


def command(cmd):
    print(cmd)
    result = commands.getstatusoutput(cmd)
    return result


def decompression_total_binary_packet(tar_path, out_path):
    os.makedirs(out_path, exist_ok=True)
    code, output = command(TAR_CMD.format(tar_path=tar_path,
                                          out_path=out_path))
    if code != 0:
        raise BaseException("decompression failed", code, output)
    return


def make_build_dir(docker_file_path, build_path):
    for filename in os.listdir(docker_file_path):
        #print build_path,filename
        subpath = os.path.join(build_path, "/images", filename)
        #print(subpath)
        os.makedirs(subpath, exist_ok=True)


#def decompression_binary_packet(out_path,)


def init():
    parser = argparse.ArgumentParser(
        description='build tidb enterprise server images.')
    parser.add_argument('--tidb-binary-packet',
                        required=True,
                        type=str,
                        help='tidb binary packet like *.tar.gz')
    parser.add_argument('--build-tmp-path',
                        required=True,
                        type=str,
                        default="/tmp/build",
                        help='tmp path of build docker images')
    parser.add_argument('--docker-file-path',
                        required=True,
                        type=str,
                        help='docker file path')
    parser.add_argument('--base-image',
                        required=True,
                        type=str,
                        help='base image name')

    args = parser.parse_args()
    return args


def main():
    args = init()
    #print(args)
    tar_path = args.tidb_binary_packet
    build_tmp_path = args.build_tmp_path
    try:
        decompression_total_binary_packet(tar_path, build_tmp_path)
        make_build_dir(args.docker_file_path, build_tmp_path)
    except BaseException(e):
        for v in e:
            print("error: %s" % v)
        raise


if __name__ == "__main__":
    main()
