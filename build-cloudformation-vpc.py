#!/usr/bin/python

##########################################################################################
#  This Python script will create Cloudformation stack in JSON using troposphere library.#
#  Account will have a 3 VPC ( Dev, Stage, Prod)                                         #
#  Account will have multi-az subnets.                                                   #
#																						 #
#  Private- No internet access                                                           #
#  Public- Outbound internet access                                                      #
#  Protected- Outbound internet access via NAT                                           #
##########################################################################################

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
    NatGateway,
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

# DEV VPC Variables

DEV_VPC_NETWORK      = "10.0.0.0/24"
DEV_VPC_PRIVATE_1    = "10.0.0.0/27"
DEV_VPC_PRIVATE_2    = "10.0.0.32/27"
DEV_VPC_PUBLIC_1     = "10.0.0.64/27"
DEV_VPC_PUBLIC_2     = "10.0.0.96/27"
DEV_VPC_PROTECTED_1  = "10.0.0.128/27"
DEV_VPC_PROTECTED_2  = "10.0.0.160/27"

t = Template()

t.set_version("2010-09-09")

t.set_description("Stack for creating a VPC with private subnets, public subnets and protected subnets")


# DEV VPC Creation

devvpc = t.add_resource(VPC(
        "DEVVPC",
        CidrBlock=DEV_VPC_NETWORK,
        InstanceTenancy="default",
        EnableDnsSupport=True,
        Tags=Tags(Name="DEV_VPC",Application=Ref("AWS::StackId"))
        )
)

# Dev Private routing table

devprivaterouteTable = t.add_resource(RouteTable(
        "DevPrivateRouteTable",
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Private_Route_Table",Application=Ref("AWS::StackId"))
        )
)

# Dev private subnetworks

devsubnetPrivate1 = t.add_resource(Subnet(
        "devprivatesubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=DEV_VPC_PRIVATE_1,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Private_Subnet_1",Application=Ref("AWS::StackId"))
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevPrivateSubnet1RouteTable",
        RouteTableId=Ref(devprivaterouteTable),
        SubnetId=Ref(devsubnetPrivate1)
        )
)

devsubnetPrivate2 = t.add_resource(Subnet(
        "devprivatesubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=DEV_VPC_PRIVATE_2,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Private_Subnet_2",Application=Ref("AWS::StackId"))
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevPrivateSubnet2RouteTable",
        RouteTableId=Ref(devprivaterouteTable),
        SubnetId=Ref(devsubnetPrivate2)
        )
)


# Dev Internet gateway

devinternetGateway = t.add_resource(InternetGateway(
        "DevInternetGateway",
        Tags=Tags(Name="Dev_IGW",Application=Ref("AWS::StackId"))
        )
)

gatewayAttachment = t.add_resource(VPCGatewayAttachment(
        "DevInternetGatewayAttachment",
        InternetGatewayId=Ref(devinternetGateway),
        VpcId=Ref(devvpc)
        )
)

# Dev Public routing table

devpublicRouteTable = t.add_resource(RouteTable(
        "DevPublicRouteTable",
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Public_Route_Table",Application=Ref("AWS::StackId"))
        )
)

devinternetRoute = t.add_resource(Route(
        "DevRouteToInternet",
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=Ref(devinternetGateway),
        RouteTableId=Ref(devpublicRouteTable),
        DependsOn=gatewayAttachment.title
        )
)

# Dev public subnetworks

devsubnetPublic1 = t.add_resource(Subnet(
        "devpublicsubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=DEV_VPC_PUBLIC_1,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Public_Subnet_1",Application=Ref("AWS::StackId"))
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevPublicSubnet1RouteTable",
        RouteTableId=Ref(devpublicRouteTable),
        SubnetId=Ref(devsubnetPublic1)
        )
)

devsubnetPublic2 = t.add_resource(Subnet(
        "devpublicsubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=DEV_VPC_PUBLIC_2,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Public_Subnet_2",Application=Ref("AWS::StackId"))
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevPublicSubnet2RouteTable",
        RouteTableId=Ref(devpublicRouteTable),
        SubnetId=Ref(devsubnetPublic2)
        )
)

# Dev protected NAT gateway

devnatgtw = t.add_resource(VPCGatewayAttachment(
        "devNatgtw",
        VpcId=Ref(devvpc),
        InternetGatewayId=Ref(devinternetGateway),
    )
)

devnateip = t.add_resource(EIP(
        "NatEip",
        Domain="devvpc",
    )
)

devnat = t.add_resource(NatGateway(
        "DevNat",
        AllocationId=GetAtt(devnateip, "AllocationId"),
        SubnetId=Ref(devsubnetPublic1),
    )
)

# Dev Protected routing table

devprotectedrouteTable = t.add_resource(RouteTable(
        "DevProtectedRouteTable",
        VpcId=Ref(devvpc),
        Tags=Tags(Name="DEV_Protected_Route_Table",Application=Ref("AWS::StackId"))
        )
)

t.add_resource(Route(
        "DevNatRoute",
        RouteTableId=Ref(devprotectedrouteTable),
        DestinationCidrBlock="0.0.0.0/0",
        NatGatewayId=Ref(devnat),
    )
)

# Dev protected subnetworks

devsubnetProtected1 = t.add_resource(Subnet(
        "devprotectedsubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=DEV_VPC_PROTECTED_1,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Protected_Subnet_1",Application=Ref("AWS::StackId"))
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevProtectedSubnet1RouteTable",
        RouteTableId=Ref(devprotectedrouteTable),
        SubnetId=Ref(devsubnetProtected1)
        )
)

devsubnetProtected2 = t.add_resource(Subnet(
        "devprotectedsubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=DEV_VPC_PROTECTED_2,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Protected_Subnet_2",Application=Ref("AWS::StackId"))
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevProtectedSubnet2RouteTable",
        RouteTableId=Ref(devprotectedrouteTable),
        SubnetId=Ref(devsubnetProtected2)
        )
)

print(t.to_json())
