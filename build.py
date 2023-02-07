# coding=utf-8

import sys

import os
import argparse
import subprocess
import logging

TAR_CMD = "tar -zxvf {tar_path} -C {out_path}"
base_image = None
mirror_path = None
work_path = None
image_namespace = None
image_version = None


def command(cmd):
    logging.info("command:[%s]", cmd)
    result = subprocess.getstatusoutput(cmd)
    return result


def parser_dockerfile(template_path, dockerfile_path, base_image):
    rf = open(template_path)
    lines = rf.read()
    rf.close()

    wf = open(dockerfile_path, "w+")
    wf.write("FROM %s\n" % (base_image,))  # add from
    wf.write(lines)
    wf.write("\n")
    wf.close()
    return


def build_image(image_name, dockerfile_path, build_path):
    CMD_Template = 'docker build --no-cache --tag="{image_name}" -f {dockerfile_path} {build_path}'
    cmd = CMD_Template.format(
        image_name=image_name, dockerfile_path=dockerfile_path, build_path=build_path)
    logging.info("build image %s", image_name)
    returnCode, output = command(cmd)
    if returnCode != 0:
        logging.critical(output)
        raise RuntimeError("build failed: %s" % output)

    logging.info("build image log success: %s", output)
    return


def init():
    parser = argparse.ArgumentParser(
        description='build tidb enterprise server images.')
    parser.add_argument('--mirror-dir',
                        required=True,
                        type=str,
                        help='please Extract all files to this path')
    parser.add_argument('--work-path',
                        required=True,
                        type=str,
                        default="/tmp/work",
                        help='work path of build docker images')
    parser.add_argument('--dockerfile-template',
                        required=True,
                        type=str,
                        nargs="+",
                        help='docker file template path')
    parser.add_argument('--base-image',
                        required=True,
                        type=str,
                        help='base image name')
    parser.add_argument('--image-namespace',
                        required=True,
                        type=str,
                        help='base image namepsace')
    parser.add_argument('--image-version',
                        required=True,
                        type=str,
                        help='base image version')

    parser.add_argument('--log-file',
                        required=False,
                        type=str,
                        help='log file name,default is stdout')

    args = parser.parse_args()
    return args


def prepare_dockerfile(dockerfile_template_path, filename, work_path):

    os.makedirs(os.path.join(work_path, "dockerfile"), exist_ok=True)

    output_path = os.path.join(work_path, "dockerfile", filename)
    parser_dockerfile(dockerfile_template_path, output_path, base_image)

    return output_path

# copy file to images


def prepare_build_file(dockerfile_path, mirror_path, build_path):
    rf = open(dockerfile_path)
    lines = rf.readlines()
    rf.close()

    cmd_list = []
    for line in lines:
        tmp_list = line.split()
        if len(tmp_list) < 3:
            continue

        if tmp_list[0] == "COPY":
            cmd_list.append("cd %s && cp -r %s %s" %
                            (mirror_path, "".join(tmp_list[1:-1]), build_path))

    os.makedirs(build_path, exist_ok=True)
    for cmd in cmd_list:
        (returnCode, output) = command(cmd)
        if returnCode != 0:
            logging.critical(output)
            raise RuntimeError(
                "prepare failed: %s" % output)
    return


def check_image(component, image_name):
    passCodes = {"tiflash": 78}  # componet:returnCode
    passCode = passCodes.get(component, 0)
    CMD_TMP = "docker run -it --rm {image_name} -h".format(
        image_name=image_name)
    (returnCode, output) = command(CMD_TMP)
    if returnCode != passCode:
        raise RuntimeError("check error for %s: %s" % (image_name, output))
    return


def build(dockerfile_template_path):
    (_, filename) = os.path.split(dockerfile_template_path)
    image_name = image_namespace+"/"+filename+":"+image_version

    logging.info("build %s start", image_name)

    dockerfile_path = prepare_dockerfile(
        dockerfile_template_path, filename, work_path)

    build_path = os.path.join(work_path, "build", filename)
    prepare_build_file(
        dockerfile_path, mirror_path, build_path)

    build_image(image_name, dockerfile_path, build_path)

    check_image(filename, image_name)
    return image_name


def main():
    global base_image
    global mirror_path
    global work_path
    global image_namespace
    global image_version

    args = init()
    # print(args)
    base_image = args.base_image
    mirror_path = args.mirror_dir
    work_path = args.work_path
    dockerfile_template_list = args.dockerfile_template

    image_namespace = args.image_namespace
    image_version = args.image_version

    LOG_FORMAT = "%(asctime)s - %(pathname)s - [%(lineno)d] - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(level=logging.DEBUG,
                        format=LOG_FORMAT,
                        datefmt=DATE_FORMAT,
                        filename=args.log_file,
                        filemode="w")

    error_list = []
    for dockerfile_template_path in dockerfile_template_list:
        try:
            print("# build image for %s start,please wait" %
                  (dockerfile_template_path,))
            image_name = build(dockerfile_template_path)
            print("# image %s build success,and check passed,you can push" %
                  (image_name))
            print("docker push %s" % image_name)
        except Exception as e:
            print("# build failed,%s,details in log,[%s]" %
                  (e, args.log_file))
            error_list.append(dockerfile_template_path)

    if len(error_list) > 0:
        print("# error list [%s]" % (" ".join(error_list),))


if __name__ == "__main__":
    main()
