import json
import logging
import argparse
from typing import List, Dict
from pydantic import BaseModel, ValidationError, Field

# Postavljanje logiranja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic modeli za striktno parsiranje i validaciju JSON podataka
class Computer(BaseModel):
    id: str = Field(..., description="Jedinstveni identifikator instance")
    name: str = Field(..., description="Naziv instance")
    networks: List[str] = Field(..., description="Lista podmreža kojima instance pripada")

class NetworkConfig(BaseModel):
    subnets: List[str] = Field(..., description="Lista podmreža u mrežnoj konfiguraciji")
    computers: List[Computer] = Field(..., description="Lista instanci računala")

# Funkcija za generiranje dinamičkog CIDR bloka
def generate_cidr_block(subnet_idx: int) -> str:
    """Generira jedinstveni CIDR blok za svaku podmrežu koristeći indeks podmreže."""
    return f"10.1.{subnet_idx}.0/24"

# Funkcija za generiranje Terraform podmreža
def generate_subnet_terraform(subnets: List[str], network_id: str) -> str:
    """Generira Terraform resurse za podmreže."""
    subnet_configs = []
    for idx, subnet in enumerate(subnets):
        cidr = generate_cidr_block(idx)
        subnet_config = f"""
resource "openstack_networking_subnet_v2" "{subnet}" {{
    network_id = {network_id}
    name = "{subnet}"
    cidr = "{cidr}"
}}
"""
        logger.debug(f"Generirana podmreža '{subnet}' s CIDR blokom '{cidr}'")
        subnet_configs.append(subnet_config)
    return "\n".join(subnet_configs)

# Funkcija za generiranje Terraform instanci
def generate_instance_terraform(computers: List[Computer], network_map: Dict[str, int], key_pair_name: str) -> str:
    """Generira Terraform resurse za instance."""
    instance_configs = []
    for computer in computers:
        network_name = computer.networks[0]

        # Provjera prisutnosti mreže u mapi
        if network_name not in network_map:
            logger.error(f"Mreža '{network_name}' nije pronađena u mapi podmreža.")
            continue  # Preskoči ovu instancu ako mreža nije pronađena

        ip_address = f"10.1.{network_map[network_name]}." + str(100 + len(instance_configs))  # Dinamička alokacija IP-a
        instance_config = f"""
resource "openstack_compute_instance_v2" "{computer.id}" {{
    name = "{computer.name}"
    image_name = "debian-12"
    flavor_name = "m1.small"
    key_pair = "{key_pair_name}"
    security_groups = ["test"]
    metadata = {{
        author = "gmail.com"
    }}

    network {{
        name = "{network_name}"
        fixed_ip_v4 = "{ip_address}"
    }}
}}
"""
        logger.debug(f"Generirana instanca '{computer.id}' s IP adresom '{ip_address}'")
        instance_configs.append(instance_config)
    return "\n".join(instance_configs)

# Glavna funkcija za generiranje Terraform konfiguracije na temelju JSON ulaza
def generate_terraform_configuration(input_json: dict, key_pair_name: str) -> str:
    """Generira kompletnu Terraform konfiguraciju za podmreže i instance."""
    try:
        # Parsiranje JSON-a u Pydantic model
        network_config = NetworkConfig(**input_json)

        # Generiranje Terraform konfiguracije za podmreže
        network_id = "openstack_networking_network_v2.demo_test_network.id"  # Primjer ID-a, može se zamijeniti stvarnom varijablom
        subnet_terraform = generate_subnet_terraform(network_config.subnets, network_id)

        # Kreiraj mapu za nazive mreža na temelju indeksa podmreža
        network_map = {network: idx for idx, network in enumerate(network_config.subnets)}

        # Generiranje Terraform konfiguracije za instance
        instance_terraform = generate_instance_terraform(network_config.computers, network_map, key_pair_name)

        # Kombiniraj obje konfiguracije (podmreže i instance)
        return subnet_terraform + "\n" + instance_terraform

    except ValidationError as e:
        logger.error("Greška pri parsiranju JSON ulaza: %s", e)
        return ""
    except KeyError as e:
        logger.error("Nedostaje ključ u JSON ulazu: %s", e)
        return ""
    except Exception as e:
        logger.error("Došlo je do neočekivane greške: %s", e)
        return ""

# Funkcija za čitanje argumenata s komandne linije
def parse_args():
    """Parsira argumente komandne linije za JSON ulaznu datoteku i izlaznu datoteku."""
    parser = argparse.ArgumentParser(description="Generiraj Terraform konfiguraciju.")
    parser.add_argument('--input', required=True, help="Putanja do JSON ulazne datoteke.")
    parser.add_argument('--output', required=True, help="Putanja do izlazne Terraform datoteke.")
    parser.add_argument('--key_pair', required=True, help="Naziv ključnog para za Terraform konfiguraciju.")
    parser.add_argument('--log_level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                        help="Razina logiranja (default: INFO).")

    return parser.parse_args()

# Postavljanje razine logiranja prema argumentima
def setup_logging(log_level: str):
    """Postavi razinu logiranja prema odabiru korisnika."""
    level = getattr(logging, log_level.upper())
    logger.setLevel(level)

# Glavna funkcija koja koristi argumente s komandne linije
def main():
    args = parse_args()
    setup_logging(args.log_level)

    try:
        # Učitaj JSON ulaznu datoteku
        with open(args.input, 'r') as f:
            input_json = json.load(f)

        # Generiraj Terraform konfiguraciju
        terraform_config = generate_terraform_configuration(input_json, args.key_pair)

        # Zapisivanje rezultata u izlaznu datoteku
        if terraform_config:
            with open(args.output, 'w') as f:
                f.write(terraform_config)
            logger.info(f"Terraform konfiguracija je uspješno generirana i spremljena u '{args.output}'")
        else:
            logger.error("Pogreška u generiranju Terraform konfiguracije.")
    except FileNotFoundError as e:
        logger.error(f"Datoteka nije pronađena: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Greška pri dekodiranju JSON-a: {e}")
    except Exception as e:
        logger.error(f"Neočekivana pogreška: {e}")

# Pokreni glavnu funkciju
if __name__ == "__main__":
    main()
