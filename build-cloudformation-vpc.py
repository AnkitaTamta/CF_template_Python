#!/usr/bin/python

##########################################################################################
#  This Python script will create Cloudformation stack in JSON using troposphere library.#
#  Account will have a 3 VPC ( Dev, Stage, Prod)                                         #
#  Account will have multi-az subnets.                                                   #
#                                                                                        #
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

##############################################################################################

# DEV environment VPC Variables

DEV_VPC_NETWORK       = "10.0.0.0/24"
DEV_VPC_PRIVATE_1     = "10.0.0.0/27"
DEV_VPC_PRIVATE_2     = "10.0.0.32/27"
DEV_VPC_PUBLIC_1      = "10.0.0.64/27"
DEV_VPC_PUBLIC_2      = "10.0.0.96/27"
DEV_VPC_PROTECTED_1   = "10.0.0.128/27"
DEV_VPC_PROTECTED_2   = "10.0.0.160/27"

# Stage environment VPC Variables

STG_VPC_NETWORK       = "10.1.0.0/18"
STG_VPC_PRIVATE_1     = "10.1.0.0/21"
STG_VPC_PRIVATE_2     = "10.1.8.0/21"
STG_VPC_PUBLIC_1      = "10.1.16.0/21"
STG_VPC_PUBLIC_2      = "10.1.24.0/21"
STG_VPC_PROTECTED_1   = "10.1.32.0/21"
STG_VPC_PROTECTED_2   = "10.1.40.0/21"

# Prod environment VPC Variables

PROD_VPC_NETWORK      = "10.2.0.0/18"
PROD_VPC_PRIVATE_1    = "10.2.0.0/21"
PROD_VPC_PRIVATE_2    = "10.2.8.0/21"
PROD_VPC_PUBLIC_1     = "10.2.16.0/21"
PROD_VPC_PUBLIC_2     = "10.2.24.0/21"
PROD_VPC_PROTECTED_1  = "10.2.32.0/21"
PROD_VPC_PROTECTED_2  = "10.2.40.0/21"

##############################################################################################

t = Template()

t.set_version("2010-09-09")

t.set_description("Stack for creating a VPC with private subnets, public subnets and protected subnets for Dev , Stg and Prod Environments")

####################################CREATING DEV ENVIRONMNET INFRA####################################

# DEV environment VPC Creation

devvpc = t.add_resource(VPC(
        "DEVVPC",
        CidrBlock=DEV_VPC_NETWORK,
        InstanceTenancy="default",
        EnableDnsSupport=True,
        Tags=Tags(Name="DEV_VPC",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Dev environment Private routing table

devprivaterouteTable = t.add_resource(RouteTable(
        "DevPrivateRouteTable",
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Private_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Dev environment private subnetworks

devsubnetPrivate1 = t.add_resource(Subnet(
        "devprivatesubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=DEV_VPC_PRIVATE_1,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Private_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
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
        Tags=Tags(Name="Dev_Private_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevPrivateSubnet2RouteTable",
        RouteTableId=Ref(devprivaterouteTable),
        SubnetId=Ref(devsubnetPrivate2)
        )
)


# Dev environment Internet gateway

devinternetGateway = t.add_resource(InternetGateway(
        "DevInternetGateway",
        Tags=Tags(Name="Dev_IGW",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

gatewayAttachment = t.add_resource(VPCGatewayAttachment(
        "DevInternetGatewayAttachment",
        InternetGatewayId=Ref(devinternetGateway),
        VpcId=Ref(devvpc)
        )
)

# Dev environment Public routing table

devpublicRouteTable = t.add_resource(RouteTable(
        "DevPublicRouteTable",
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Public_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
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

# Dev environment public subnetworks

devsubnetPublic1 = t.add_resource(Subnet(
        "devpublicsubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=DEV_VPC_PUBLIC_1,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Public_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
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
        Tags=Tags(Name="Dev_Public_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevPublicSubnet2RouteTable",
        RouteTableId=Ref(devpublicRouteTable),
        SubnetId=Ref(devsubnetPublic2)
        )
)

# Dev environment protected NAT gateway

devnatgtw = t.add_resource(VPCGatewayAttachment(
        "devNatgtw",
        VpcId=Ref(devvpc),
        InternetGatewayId=Ref(devinternetGateway),
        )
)

devnateip = t.add_resource(EIP(
        "DevNatEip",
        Domain="devvpc",
                Tags=Tags(Name="Dev_EIP",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

devnat = t.add_resource(NatGateway(
        "DevNat",
        AllocationId=GetAtt(devnateip, "AllocationId"),
        SubnetId=Ref(devsubnetPublic1),
                Tags=Tags(Name="Dev_NAT",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Dev environment Protected routing table

devprotectedrouteTable = t.add_resource(RouteTable(
        "DevProtectedRouteTable",
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Protected_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(Route(
        "DevNatRoute",
        RouteTableId=Ref(devprotectedrouteTable),
        DestinationCidrBlock="0.0.0.0/0",
        NatGatewayId=Ref(devnat),
        )
)

# Dev environment protected subnetworks

devsubnetProtected1 = t.add_resource(Subnet(
        "devprotectedsubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=DEV_VPC_PROTECTED_1,
        VpcId=Ref(devvpc),
        Tags=Tags(Name="Dev_Protected_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
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
        Tags=Tags(Name="Dev_Protected_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "DevProtectedSubnet2RouteTable",
        RouteTableId=Ref(devprotectedrouteTable),
        SubnetId=Ref(devsubnetProtected2)
        )
)

######################################END OF DEV ENVIRONMNET INFRA######################################

####################################CREATING STAGE ENVIRONMNET INFRA####################################

# STAGE environment VPC Creation

stgvpc = t.add_resource(VPC(
        "STGVPC",
        CidrBlock=STG_VPC_NETWORK,
        InstanceTenancy="default",
        EnableDnsSupport=True,
        EnableDnsHostnames=True,
        Tags=Tags(Name="STG_VPC",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Stage environment Private routing table

stgprivaterouteTable = t.add_resource(RouteTable(
        "StgPrivateRouteTable",
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Private_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Stage environment private subnetworks

stgsubnetPrivate1 = t.add_resource(Subnet(
        "stgprivatesubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=STG_VPC_PRIVATE_1,
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Private_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "StgPrivateSubnet1RouteTable",
        RouteTableId=Ref(stgprivaterouteTable),
        SubnetId=Ref(stgsubnetPrivate1)
        )
)

stgsubnetPrivate2 = t.add_resource(Subnet(
        "stgprivatesubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=STG_VPC_PRIVATE_2,
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Private_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "StgPrivateSubnet2RouteTable",
        RouteTableId=Ref(stgprivaterouteTable),
        SubnetId=Ref(stgsubnetPrivate2)
        )
)

# Stg environment Internet gateway

stginternetGateway = t.add_resource(InternetGateway(
        "StgInternetGateway",
        Tags=Tags(Name="Stg_IGW",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

gatewayAttachment = t.add_resource(VPCGatewayAttachment(
        "StgInternetGatewayAttachment",
        InternetGatewayId=Ref(stginternetGateway),
        VpcId=Ref(stgvpc)
        )
)

# Stage environment Public routing table

stgpublicRouteTable = t.add_resource(RouteTable(
        "StgPublicRouteTable",
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Public_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

stginternetRoute = t.add_resource(Route(
        "StgRouteToInternet",
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=Ref(stginternetGateway),
        RouteTableId=Ref(stgpublicRouteTable),
        DependsOn=gatewayAttachment.title
        )
)

# Stage environment public subnetworks

stgsubnetPublic1 = t.add_resource(Subnet(
        "stgpublicsubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=STG_VPC_PUBLIC_1,
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Public_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "StgPublicSubnet1RouteTable",
        RouteTableId=Ref(stgpublicRouteTable),
        SubnetId=Ref(stgsubnetPublic1)
        )
)

stgsubnetPublic2 = t.add_resource(Subnet(
        "stgpublicsubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=STG_VPC_PUBLIC_2,
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Public_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "StgPublicSubnet2RouteTable",
        RouteTableId=Ref(stgpublicRouteTable),
        SubnetId=Ref(stgsubnetPublic2)
        )
)

# Stage environment protected NAT gateway

stgnatgtw = t.add_resource(VPCGatewayAttachment(
        "stgNatgtw",
        VpcId=Ref(stgvpc),
        InternetGatewayId=Ref(stginternetGateway),
        )
)

stgnateip = t.add_resource(EIP(
        "StgNatEip",
        Domain="stgvpc",
            Tags=Tags(Name="Stg_EIP",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

stgnat = t.add_resource(NatGateway(
        "StgNat",
        AllocationId=GetAtt(stgnateip, "AllocationId"),
        SubnetId=Ref(stgsubnetPublic1),
            Tags=Tags(Name="Stg_NAT",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Stage environment Protected routing table

stgprotectedrouteTable = t.add_resource(RouteTable(
        "StgProtectedRouteTable",
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Protected_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(Route(
        "StgNatRoute",
        RouteTableId=Ref(stgprotectedrouteTable),
        DestinationCidrBlock="0.0.0.0/0",
        NatGatewayId=Ref(stgnat),
        )
)

# Stage environment protected subnetworks

stgsubnetProtected1 = t.add_resource(Subnet(
        "stgprotectedsubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=STG_VPC_PROTECTED_1,
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Protected_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "StgProtectedSubnet1RouteTable",
        RouteTableId=Ref(stgprotectedrouteTable),
        SubnetId=Ref(stgsubnetProtected1)
        )
)

stgsubnetProtected2 = t.add_resource(Subnet(
        "stgprotectedsubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=STG_VPC_PROTECTED_2,
        VpcId=Ref(stgvpc),
        Tags=Tags(Name="Stg_Protected_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "StgProtectedSubnet2RouteTable",
        RouteTableId=Ref(stgprotectedrouteTable),
        SubnetId=Ref(stgsubnetProtected2)
        )
)

######################################END OF STAGE ENVIRONMNET INFRA#######################################

######################################CREATING PROD ENVIRONMNET INFRA######################################

# PROD environment VPC Creation

prodvpc = t.add_resource(VPC(
        "PRODVPC",
        CidrBlock=PROD_VPC_NETWORK,
        InstanceTenancy="default",
        EnableDnsSupport=True,
        EnableDnsHostnames=True,
        Tags=Tags(Name="PROD_VPC",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Prod environment Private routing table

prodprivaterouteTable = t.add_resource(RouteTable(
        "ProdPrivateRouteTable",
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Private_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Stage environment private subnetworks

prodsubnetPrivate1 = t.add_resource(Subnet(
        "prodprivatesubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=PROD_VPC_PRIVATE_1,
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Private_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "ProdPrivateSubnet1RouteTable",
        RouteTableId=Ref(prodprivaterouteTable),
        SubnetId=Ref(prodsubnetPrivate1)
        )
)

prodsubnetPrivate2 = t.add_resource(Subnet(
        "prodprivatesubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=PROD_VPC_PRIVATE_2,
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Private_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "ProdPrivateSubnet2RouteTable",
        RouteTableId=Ref(prodprivaterouteTable),
        SubnetId=Ref(prodsubnetPrivate2)
        )
)

# Prod environment Internet gateway

prodinternetGateway = t.add_resource(InternetGateway(
        "ProdInternetGateway",
        Tags=Tags(Name="Prod_IGW",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

gatewayAttachment = t.add_resource(VPCGatewayAttachment(
        "ProdInternetGatewayAttachment",
        InternetGatewayId=Ref(prodinternetGateway),
        VpcId=Ref(prodvpc)
        )
)

# Prod environment Public routing table

prodpublicRouteTable = t.add_resource(RouteTable(
        "ProdPublicRouteTable",
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Public_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

ProdinternetRoute = t.add_resource(Route(
        "ProdRouteToInternet",
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=Ref(prodinternetGateway),
        RouteTableId=Ref(prodpublicRouteTable),
        DependsOn=gatewayAttachment.title
        )
)

# Prod environment public subnetworks

ProdsubnetPublic1 = t.add_resource(Subnet(
        "prodpublicsubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=PROD_VPC_PUBLIC_1,
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Public_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "ProdPublicSubnet1RouteTable",
        RouteTableId=Ref(prodpublicRouteTable),
        SubnetId=Ref(ProdsubnetPublic1)
        )
)

prodsubnetPublic2 = t.add_resource(Subnet(
        "prodpublicsubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=PROD_VPC_PUBLIC_2,
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Public_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "ProdPublicSubnet2RouteTable",
        RouteTableId=Ref(prodpublicRouteTable),
        SubnetId=Ref(prodsubnetPublic2)
        )
)

# Prod environment protected NAT gateway

prodnatgtw = t.add_resource(VPCGatewayAttachment(
        "prodNatgtw",
        VpcId=Ref(prodvpc),
        InternetGatewayId=Ref(prodinternetGateway),
        )
)

prodnateip = t.add_resource(EIP(
        "ProdNatEip",
        Domain="prodvpc",
            Tags=Tags(Name="Prod_EIP",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

prodnat = t.add_resource(NatGateway(
        "ProdNat",
        AllocationId=GetAtt(prodnateip, "AllocationId"),
        SubnetId=Ref(prodsubnetPublic1),
            Tags=Tags(Name="Prod_NAT",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

# Prod environment Protected routing table

prodprotectedrouteTable = t.add_resource(RouteTable(
        "ProdProtectedRouteTable",
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Protected_Route_Table",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(Route(
        "ProdNatRoute",
        RouteTableId=Ref(prodprotectedrouteTable),
        DestinationCidrBlock="0.0.0.0/0",
        NatGatewayId=Ref(prodnat),
        )
)

# Prod environment protected subnetworks

prodsubnetProtected1 = t.add_resource(Subnet(
        "prodprotectedsubnet1",
        AvailabilityZone=Select(0, GetAZs()),
        CidrBlock=PROD_VPC_PROTECTED_1,
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Protected_Subnet_1",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "ProdProtectedSubnet1RouteTable",
        RouteTableId=Ref(prodprotectedrouteTable),
        SubnetId=Ref(prodsubnetProtected1)
        )
)

prodsubnetProtected2 = t.add_resource(Subnet(
        "prodprotectedsubnet2",
        AvailabilityZone=Select(1, GetAZs()),
        CidrBlock=PROD_VPC_PROTECTED_2,
        VpcId=Ref(prodvpc),
        Tags=Tags(Name="Prod_Protected_Subnet_2",Application=Ref("AWS::StackId"),CostCenter="12345")
        )
)

t.add_resource(SubnetRouteTableAssociation(
        "ProdProtectedSubnet2RouteTable",
        RouteTableId=Ref(prodprotectedrouteTable),
        SubnetId=Ref(prodsubnetProtected2)
        )
)

######################################END OF PROD ENVIRONMNET INFRA########################################

print(t.to_json())
