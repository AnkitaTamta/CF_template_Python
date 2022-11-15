#!/usr/bin/python

from troposphere import (
    GetAZs,
    Select,
    GetAtt,
    Output,
    Parameter,
    Ref,
    Tags,
    Template,
)
from troposphere.ec2 import (
    EIP,
    VPC,
    InternetGateway,
    NetworkAcl,
    NetworkAclEntry,
    NetworkInterfaceProperty,
    PortRange,
    Route,
    RouteTable,
    Subnet,
    SubnetNetworkAclAssociation,
    SubnetRouteTableAssociation,
    VPCGatewayAttachment,
)
from troposphere.policies import CreationPolicy, ResourceSignal

VPC_NETWORK   = "10.1.0.0/18"
VPC_PRIVATE_1 = "10.1.0.0/20"
VPC_PRIVATE_2 = "10.1.16.0/20"
VPC_PUBLIC_1  = "10.1.32.0/20"
VPC_PUBLIC_2  = "10.1.48.0/20"

t = Template()

t.set_version("2010-09-09")

t.set_description("Stack for creating a basic VPC with private and public Subnets")


# VPC Creation

VPC = t.add_resource(VPC(
      "VPC",
        CidrBlock=VPC_NETWORK,
        InstanceTenancy="default",
        EnableDnsSupport=True,
        Tags=Tags(Name="TestVPC",Application=Ref("AWS::StackId"))
        )
)

# Private routing table

privaterouteTable = t.add_resource(RouteTable(
        "PrivateRouteTable",
        VpcId=Ref(VPC),
        Tags=Tags(Name="Private_Route_Table",Application=Ref("AWS::StackId"))
        )
)

# private subnetworks

subnetPrivate1 = t.add_resource(Subnet(
        "privatesubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=VPC_PRIVATE_1,
        VpcId=Ref(VPC),
        Tags=Tags(Name="Private_Subnet_1",Application=Ref("AWS::StackId"))
        )
)


t.add_resource(SubnetRouteTableAssociation(
        "PrivateSubnet1RouteTable",
        RouteTableId=Ref(privaterouteTable),
        SubnetId=Ref(subnetPrivate1)
        )
)

subnetPrivate2 = t.add_resource(Subnet(
        "privatesubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=VPC_PRIVATE_2,
        VpcId=Ref(VPC),
        Tags=Tags(Name="Private_Subnet_2",Application=Ref("AWS::StackId"))
        )
)


t.add_resource(SubnetRouteTableAssociation(
        "PrivateSubnet2RouteTable",
        RouteTableId=Ref(privaterouteTable),
        SubnetId=Ref(subnetPrivate2)
        )
)

print(t.to_json())
