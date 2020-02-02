# aws_loot

Searches an AWS environment looking for secrets, by enumerating environment variables and source code. This tool allows quick enumeration over large sets of AWS instances and services.

![](screenshot/tool.gif)

## Install

```
pip install -r requirements.txt
```
An AWS credential file (.aws/credentials) is required for authentication to the target environment
   - Access Key
   - Access Key Secret 

## How it works

Awsloot works by going through EC2, Lambda, CodeBuilder instances and searching for high entropy strings. The EC2 Looter works by querying all available instance ID's in all regions and requesting instance's USERDATA where often developers leave secrets. 
The Lambda looter operates across regions as well. Lambada looter can search all available versions of a found function. 
It starts by searching the functions environment variables then downloads the source code and scans the source for secrets. 
The Codebuilder Looter works by searching for build instances and searching those builds for environment variables that might contain secrets.

## Usage
```
Python3 awsloot.py 
```
 
## Next Features
  - Allow users to specify an ARN to scan
  - Looter for additional services 

  


