import base64
from looters.helpers.Entropy import contains_secret
from looters.helpers.Color import Color as Color
from botocore.exceptions import ClientError


class Ec2Looter:

    def __init__(self, session, threshold, regions):

        self.session = session
        self.threshold = threshold
        self.regions = regions

    def run(self):
        try:
            Color.print(Color.BLUE, "Searching Regions for EC2 Instances")

            # Go through all the regions that have EC2
            for region in self.get_regions():

                # Get all Ids in region
                ec2_in_region = self.get_instance_ids(region)

                # If there is an EC2 in that Region
                if ec2_in_region:

                    print(f'\tChecking {len(ec2_in_region)} EC2 in {region}')

                    # Go through all EC2 for that region and get USERDATA
                    for instance_id in ec2_in_region:
                        # TODO Make output consistent
                        loot = []
                        # Pull USERDATA for Instanced ID
                        user_data = self.get_instance_userdata(instance_id, region)

                        if user_data:
                            loot = [item for item in user_data.split() if contains_secret(item, THRESHOLD=self.threshold)]

                        # Print secrets if found
                        if loot:
                            print(f"\n\t{'-'*10} {instance_id} {'-'*10}")
                            [Color.print(Color.GREEN, f"\t\t[+] {item}") for item in loot if loot]

        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDeniedException':
                Color.print(Color.RED, f'[-] {e}')

    def get_instance_userdata(self, instance_id, region):
        ec2 = self.session.client('ec2', region_name=region)
        raw_data = ec2.describe_instance_attribute(Attribute='userData', InstanceId=instance_id)[
            'UserData']

        if raw_data:
            user_data = base64.b64decode(raw_data['Value']).decode("utf-8")
            return user_data
        else:
            return None


    def get_instance_ids(self, region):
        ids = []
        try:
            ec2 = self.session.client('ec2', region_name=region)
            data = ec2.describe_instances()

            for r in data['Reservations']:
                for i in r['Instances']:
                    ids.append(i['InstanceId'])
        except:
            print(f"Failed on {region}")
        return ids

    def get_regions(self):
        regions = []
        ec2 = self.session.client('ec2', region_name='us-west-2')
        for reg in ec2.describe_regions()["Regions"]:
            if reg['RegionName'] in self.regions:
                regions.append(reg['RegionName'])
        return regions
