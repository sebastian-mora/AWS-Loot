from botocore.exceptions import ClientError

from looters.helpers.Entropy import contains_secret
from looters.helpers.Color import Color as Color
import requests
import zipfile
import os
import re

'''
    BOTO3 Issue? (https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.list_functions)
    Documentation lists you can use MASTERREGION='ALL' to search all regions. I think this is bugged bc it only returns
    empty lists. This might be a conflicting with the client requirement of a region. I will open an issue on github 
'''


class LambdaLooter:

    def __init__(self, session, output, threshold, regions):
        self.session = session
        self.o_path = output
        self.regions = regions
        self.lambd_threshold_evn = threshold
        self.lambd_threshold_source = self.lambd_threshold_evn + .3
        self.pattern = "(#.*|//.*|\\\".*\\\"|'.*'|/\\*.*)"


    def run(self):
        try:
            Color.print(Color.BLUE, "\nSearching Regions for Lambda Functions")
            print(f'\tSource Code will be saved to "output/{self.o_path}"')

            for region in self.regions:

                function_id = self.get_function_ids(region)

                if function_id:
                    print(f"\tSearching {len(function_id)} in {region} Lambda Functions")

                for id in function_id:
                    loot = []
                    # Get Lambda data (EVN Vars)
                    environment_vars = self.get_function_data(id[1], region)

                    # Find and Store Sensitive ENV Vars
                    [loot.append(f"EVN_VAR - {key}: {environment_vars[key]}")
                     for key in environment_vars if contains_secret(environment_vars[key], THRESHOLD=self.lambd_threshold_evn)]

                    # Download and load function source code
                    source_data = self.get_function_source(id, region)


                    # Search Source code and save secrets
                    # This part uses Regex to find "target" areas then searches those areas by word
                    for key in self.get_function_source(id, region):

                        for line in re.findall(self.pattern, source_data[key]):

                            [loot.append(f"IN_SOURCE - {line}") for word in line.split()
                             if contains_secret(word, self.lambd_threshold_source)]

                    # Print ID and Saved Loot
                    if loot:
                        print(f"\n\t{'-' * 10} {id} {'-' * 10}")

                        [Color.print(Color.GREEN, f"\t\t[+] {item}") for item in loot if loot]
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDeniedException':
                Color.print(Color.RED, f'[-] {e}')

    def get_function_ids(self, region):
        """
        Returns list [ (Name, ARN) , (Name, ARN) ]
        """
        try:
            lambda_client = self.session.client('lambda', region_name=region)
            data = lambda_client.list_functions(FunctionVersion='ALL')['Functions']
            return [(function['FunctionName'], function['FunctionArn']) for function in data]
        except:
            return []

    def get_function_data(self, id, region):
        """
        Returns a dict of environment vars
        """
        lambda_client = self.session.client('lambda', region_name=region)
        data = lambda_client.get_function_configuration(FunctionName=id)

        try:
            return data['Environment']['Variables']
        except KeyError:
            return {}

    def get_function_source(self, id, region):
        lambda_client = self.session.client('lambda', region_name=region)
        source = lambda_client.get_function(FunctionName=id[1])
        try:
            # Get Link and setup file name
            source_loc = source["Code"]['Location']
            fname = source_loc.split('/')

            # Download File from URL
            r = requests.get(source_loc, stream=True)

            # Write Zip to output file
            fname = os.path.join(f'output/{self.o_path}', f'{fname[len(fname) - 1][:30]}.zip')
            zfile = open(fname, 'wb')
            zfile.write(r.content)
            zfile.close()

            # Load Zip contents into memory
            lambda_zip = zipfile.ZipFile(fname)

            return {id: lambda_zip.read(name).decode("utf-8") for name in lambda_zip.namelist()}

        except KeyError:
            print(Color.RED, f'Error getting {id[0]} Source')
