#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
from PyInquirer import (prompt, style_from_dict, Token)

import boto3, botocore.exceptions

from os import makedirs

from looters import EC2Looter, CodeBuildLooter, LambdaLooter
from looters.helpers.Color import Color as Color

custom_style = style_from_dict({
    Token.Separator: '#6C6C6C',
    Token.QuestionMark: '#FF9D00 bold',
    #Token.Selected: '',  # default
    Token.Selected: '#5F819D',
    Token.Pointer: '#FF9D00 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#5F819D bold',
    Token.Question: '',
})



def banner():
    print('''

     ___        ______       _                _   
    / \ \      / / ___|     | |    ___   ___ | |_ 
   / _ \ \ /\ / /\___ \     | |   / _ \ / _ \| __|
  / ___ \ V  V /  ___) |    | |__| (_) | (_) | |_ 
 /_/   \_\_/\_/  |____/     |_____\___/ \___/ \__|
                                                  

            By  Sebastian Mora                         
    ''')


def create_session(profile):
    # Ask the user for the creds

    # Create the root session# and test to see if the session is valid

    try:
        session = boto3.Session(profile_name=profile)
        session.client('sts').get_caller_identity()
        # Create output file
        create_output(profile)
        return session, profile
    # Session failed. Exit
    except botocore.exceptions.ClientError:
        Color.print(Color.RED, "[-] AWS was not able to validate the provided access credentials")
        exit(1)
    except botocore.exceptions.ProfileNotFound:
        Color.print(Color.RED, f'[-] The config profile {profile.upper()} could not be found ')
        exit(1)


def create_output(session_name):
    # Creates a folder using the profile name.
    try:
        makedirs(f'output/{session_name}')
    except FileExistsError:
        pass


def ask_profile():
    questions = [
        {
            'type': 'input',
            'name': 'profile_name',
            'message': 'AWS profile name',
        }
    ]

    return prompt(questions, style=custom_style)['profile_name']


def ask_entropy():
    value = None
    question = [{'type': 'input',
                 'name': 'threshold',
                 'message': f'Set the entropy threshold for the looters.',
                 'default': '3.5'}]

    try:
        value = float(prompt(question)['threshold'])
    except ValueError:
        Color.print(Color.RED, '[-] Invalid entry')
        exit(1)

    return value


def ask_services():
    questions = [
        {
            'type': 'checkbox',
            'message': 'Select services to L00t',
            'name': 'services',
            'choices': [{"name": "ec2"}, {"name": "lambda"}, {"name": "codebuild"}]
        }
    ]
    return prompt(questions, style=custom_style)['services']


def ask_regions():

    questions = [

        {
            'type': 'checkbox',
            'message': f'select regions to l00t',
            'name': 'regions',
            'choices': [{"name": "us-east-1"}, {"name": "us-east-2"}, {"name": "us-west-1"}, {"name": "us-west-2"},
                        {"name": "ap-east-1"}, {"name": "ap-south-1"},
                        {"name": "ap-northeast-3"}, {"name": "ap-northeast-2"}, {"name": "ap-southeast-1"},
                        {"name": "ap-southeast-2"}, {"name": "ap-northeast-1"},
                        {"name": "ca-central-1"}, {"name": "cn-north-1"}, {"name": "cn-northwest-1"},
                        {"name": "eu-central-1"}, {"name": "eu-west-1"},
                        {"name": "eu-west-2"}, {"name": "eu-west-3"}, {"name": "eu-north-1"},
                        {"name": "me-south-1"}, {"name": "sa-east-1"}]
        }
    ]

    return prompt(questions, style=custom_style)['regions']

if __name__ == '__main__':

    banner()


    profile = ask_profile()

    session, output_path = create_session(profile)

    services = ask_services()

    entropy_threshold = ask_entropy()

    regions = ask_regions()

    print('\n')

    for service in services:

        if service is 'ec2':
            EC2Looter.Ec2Looter(session, entropy_threshold, regions).run()
        if service is 'lambda':
            LambdaLooter.LambdaLooter(session, profile, entropy_threshold, regions).run()
        if service is 'codebuild':
            CodeBuildLooter.CodeBuilder(session, entropy_threshold, regions).run()
        else:
            pass
