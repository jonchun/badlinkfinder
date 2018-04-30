#!/usr/bin/env python3
# coding: utf-8

import logging

core_logger = logging.getLogger('blf')
logger = logging.getLogger('blf.output')

output_file = None
include_inbound = False

def configure(args):
    global core_logger
    global include_inbound
    global output_file

    set_logger(args.log_level)

    if args.output_file:
        output_file = args.output_file
        file_handler = logging.FileHandler(output_file)
        core_logger.addHandler(file_handler) 

    if args.include_inbound:
        include_inbound = args.include_inbound

def set_logger(level):
    global core_logger
    core_logger.setLevel(level)
    core_logger.addHandler(logging.StreamHandler())

def display(crawler, errors):
    core_logger.setLevel(logging.INFO)
    if not errors:
        core_logger.info('No Issues Found!')
    else:
        core_logger.info('Here are the issues that were found:')
        for error in errors:
            error.include_inbound = include_inbound
            core_logger.info(error)
        # Output file
        if output_file:
            core_logger.info('\nSaving log to "{}"...'.format(output_file))
