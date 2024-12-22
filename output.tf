
resource "openstack_networking_subnet_v2" "network_1" {
    network_id = openstack_networking_network_v2.demo_test_network.id
    name = "network_1"
    cidr = "10.1.0.0/24"
}


resource "openstack_networking_subnet_v2" "network_2" {
    network_id = openstack_networking_network_v2.demo_test_network.id
    name = "network_2"
    cidr = "10.1.1.0/24"
}


resource "openstack_compute_instance_v2" "test_1" {
    name = "First computer"
    image_name = "debian-12"
    flavor_name = "m1.small"
    key_pair = "my_key"
    security_groups = ["test"]
    metadata = {
        author = "gmail.com"
    }

    network {
        name = "network_1"
        fixed_ip_v4 = "10.1.0.100"
    }
}


resource "openstack_compute_instance_v2" "test_2" {
    name = "Second computer"
    image_name = "debian-12"
    flavor_name = "m1.small"
    key_pair = "my_key"
    security_groups = ["test"]
    metadata = {
        author = "gmail.com"
    }

    network {
        name = "network_1"
        fixed_ip_v4 = "10.1.0.101"
    }
}


resource "openstack_compute_instance_v2" "test_3" {
    name = "Third computer"
    image_name = "debian-12"
    flavor_name = "m1.small"
    key_pair = "my_key"
    security_groups = ["test"]
    metadata = {
        author = "gmail.com"
    }

    network {
        name = "network_2"
        fixed_ip_v4 = "10.1.1.102"
    }
}
