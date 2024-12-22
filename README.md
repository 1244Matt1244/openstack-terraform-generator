# Terraform Konfiguracija za OpenStack Resurse

Ova skripta (`2024_11_06_test.py`) generira Terraform konfiguraciju za mrežne resurse u OpenStack-u na temelju ulazne JSON datoteke s podacima o mrežnim podmrežama i računalnim instancama.

## Funkcionalnosti

Skripta automatski generira:

1. **OpenStack mrežne subnete** s jedinstvenim CIDR blokovima.
2. **Računalne instance** povezane s odgovarajućim podmrežama, s dinamički dodijeljenim statičkim IP adresama.

## Instalacija ovisnosti

Potrebne biblioteke za rad:

- `argparse` i `json` (ugrađene u Python).
- `pydantic` za validaciju JSON podataka:
  ```bash
  pip install pydantic
  ```

## Struktura JSON Ulazne Datoteke

Primjer JSON datoteke koju skripta očekuje:

```json
{
  "subnets": ["network_1", "network_2"],
  "computers": [
    {
      "id": "server_1",
      "name": "web-server",
      "networks": ["network_1"]
    },
    {
      "id": "server_2",
      "name": "db-server",
      "networks": ["network_2"]
    }
  ]
}
```

### Polja:

- `subnets`: Lista imena podmreža.
- `computers`: Lista instanci s `id`, `name`, i `networks` atributima.

## Korištenje Skripte

Pokretanje iz komandne linije:

```bash
python 2024_11_06-test.py --input <input_file> --output <output_file> --key_pair <key_pair_name> [--log_level <level>]
```

### Argumenti

- `--input`: Putanja do JSON datoteke s ulaznim podacima.
- `--output`: Putanja do izlazne Terraform datoteke.
- `--key_pair`: Naziv OpenStack ključnog para.
- `--log_level`: (Opcionalno) Razina logiranja (`INFO`, `DEBUG`, `ERROR`). Default je `INFO`.

## Primjer Izlazne Konfiguracije

Izlazna datoteka sadrži konfiguraciju poput ove:

```hcl
resource "openstack_networking_subnet_v2" "network_1" {
    network_id = openstack_networking_network_v2.demo_test_network.id
    name = "network_1"
    cidr = "10.1.0.0/24"
}

resource "openstack_compute_instance_v2" "server_1" {
    name = "web-server"
    image_name = "debian-12"
    ...
    network {
        name = "network_1"
        fixed_ip_v4 = "10.1.0.100"
    }
}
```

## Logiranje i Provjera Grešaka

Razina logiranja može se odrediti pomoću `--log_level` argumenta (`INFO`, `DEBUG`, itd.). Skripta obavještava o problemima s JSON strukturom, nedostajućim podacima, ili greškama prilikom generiranja konfiguracije.
