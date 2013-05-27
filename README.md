#ny

Ny is an opinionated deployment and server management cli.

## Installation
```
pip install ny
```

## How to Use
```
# Spin up a frontend instance in production
ny vm create -t frontend production

# List Instances in the Production environment
ny vm list production staging

# Terminate an instance
ny vm terminate -i i-xxxxxxxx
```

## Configuration
Ny is controlled via a per-project `Nyfile`, which allows for simple configuration via TOML. Ny allows you to define
multiple deploy environments and instance templates.

Deployment environments allow you to separate your Staging and Production environemnts, and easily deploy and manage
VMs in both. Different environments are expected to each be a unique VPC.

Instance templates allow the configuration of parameters such as `image_id`, `security_groups`, and `bootscripts`.

Here is an example configuration file:

```toml
[global]
  # Path relative to Nyfile to bootscripts folder
  bootscripts = "bootscripts"

[envs]
  [envs.production]
    vpc = "vpc-xxxxxxxx"
    key = "keypair-name"

    gateway = "SOME_IP_ADDRESS"

    subnets = [
      "subnet-xxxxxxxx",
      "subnet-yyyyyyyy",
    ]

    security_groups = [
      "Security Group Name => sg-xxxxyyyy",
      "Frontend Security Group => sg-xyxyxyxy",
    ]

    [envs.production.salt]
      # Saltstack master server
      master = "10.x.x.x"

[types]
  [types.frontend]
    image_id = "ami-1234xxxx"
    type = "t1.micro"
    security_groups = [
      "Security Group Name",
      "Frontend Security Group",
    ]

    # Relative to the global bootscript variable if set
    # Available vars: env
    bootscripts = [
      "common/common_script",
      "common/install-salt-minion",
    ]
```

## License
Copyright (c) 2013 Judson Stephenson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
