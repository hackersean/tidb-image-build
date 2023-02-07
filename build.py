# coding=utf-8

import sys

import os
import argparse
import subprocess
import logging

TAR_CMD = "tar -zxvf {tar_path} -C {out_path}"


def command(cmd):
    logging.debug("command:[%s]", cmd)
    result = subprocess.getstatusoutput(cmd)
    return result


def decompression_total_binary_packet(tar_path, out_path):
    os.makedirs(out_path, exist_ok=True)
    code, output = command(TAR_CMD.format(tar_path=tar_path,
                                          out_path=out_path))
    if code != 0:
        raise BaseException("decompression failed", code, output)
    return


def make_build_dir(component_lsit, build_path):
    for filename in component_lsit:
        # print build_path,filename
        subpath = os.path.join(build_path, "images", filename)
        # print(subpath)
        os.makedirs(subpath, exist_ok=True)


def decompression_every_binary_packet(component_lsit, tar_path, build_path):
    _, tar_filename = os.path.split(tar_path)
    tar_dir = os.path.join(build_path,
                           tar_filename.split(".tar.gz")[0])
    for file in os.listdir(tar_dir):
        if file.endswith(".tar.gz"):
            print(file.split("-v")[0])
    print("\n")
    for name in component_lsit:
        print(name)


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
    # print(args)
    tar_path = args.tidb_binary_packet
    build_tmp_path = args.build_tmp_path
    try:
        component_lsit = os.listdir(args.docker_file_path)
        logging.info("decompression %s", tar_path)
        # decompression_total_binary_packet(tar_path, build_tmp_path)
        make_build_dir(component_lsit, build_tmp_path)
        logging.info("complete decompression %s", tar_path)
        decompression_every_binary_packet(
            component_lsit, tar_path, build_tmp_path)
    except BaseException:
        raise


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(level=logging.DEBUG,
                        format=LOG_FORMAT, datefmt=DATE_FORMAT)

    main()
