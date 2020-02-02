from botocore.exceptions import ClientError, EndpointConnectionError
from looters.helpers.Entropy import contains_secret
from looters.helpers.Color import Color


class CodeBuilder:

    def __init__(self, session, threshold, regions):
        self.session = session
        self.threshold = threshold
        self.regions = regions

    def run(self):

        Color.print(Color.BLUE, "\nSearching Regions for Codebuilds")
        for region in self.regions:
            try:
                ids = self.get_build_id(region)

                if ids:
                    env_vars = self.get_environment_vars(ids, region)
                    print(f"\tSearching {len(env_vars)} Builds in {region} \n")
                    for build in env_vars:
                        loot = []
                        [loot.append(var) for var in env_vars[build] if contains_secret(var['value'], THRESHOLD=self.threshold)]

                        if loot:
                            print(f"\t{'-' * 10} {build} {'-' * 10}")
                            [Color.print(Color.GREEN, f'\t\t[+] {item}') for item in loot]

            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDeniedException':
                    Color.print(Color.RED, f'\n\t[-] {e}')
            except EndpointConnectionError as e:
                #Color.print(Color.RED, f'\n\t[-] {e}')
                pass

    def get_build_id(self, region):
        try:
            code_sess = self.session.client('codebuild', region_name=region)
            ids = code_sess.list_builds()
            return ids['ids']
        except ClientError as e:
            return []

    def get_environment_vars(self, id, region):
        code_sess = self.session.client('codebuild', region_name=region)
        raw = code_sess.batch_get_builds(ids=id)
        return {build['arn']: build['environment']['environmentVariables'] for build in raw['builds']}
