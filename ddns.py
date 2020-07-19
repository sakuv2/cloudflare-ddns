#!/usr/bin/env python
"""Cloudflare API code - example"""

import CloudFlare
import pydantic
import requests


class Env(pydantic.BaseSettings):
    email: str
    token: str
    zoon: str
    dns_name: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def my_ip_address():
    """Cloudflare API code - example"""

    urls = [
        "https://api.ipify.org",
        "http://myip.dnsomatic.com",
        "http://www.trackip.net/ip",
        "http://myexternalip.com/raw",
    ]
    ip_address = ""
    for url in urls:
        try:
            ip_address = requests.get(url).text
        except Exception:
            continue
        if ip_address != "":
            break

    if ip_address == "":
        exit("Get ip address: failed")

    ip_address_type = "AAAA" if ":" in ip_address else "A"

    return ip_address, ip_address_type


def do_dns_update(cf, zone_id, dns_name, ip_address, ip_address_type):
    """Cloudflare API code - example"""

    try:
        params = {"name": dns_name, "match": "all", "type": ip_address_type}
        dns_records = cf.zones.dns_records.get(zone_id, params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit("/zones/dns_records %s - %d %s - api call failed" % (dns_name, e, e))

    updated = False

    # update the record - unless it's already correct
    for dns_record in dns_records:
        old_ip_address = dns_record["content"]
        old_ip_address_type = dns_record["type"]

        if ip_address_type not in ["A", "AAAA"]:
            # we only deal with A / AAAA records
            continue

        if ip_address_type != old_ip_address_type:
            # only update the correct address type (A or AAAA)
            # we don't see this becuase of the search params above
            print("IGNORED: %s %s ; wrong address family" % (dns_name, old_ip_address))
            continue

        if ip_address == old_ip_address:
            print("UNCHANGED: %s %s" % (dns_name, ip_address))
            updated = True
            continue

        proxied_state = dns_record["proxied"]

        # Yes, we need to update this record - we know it's the same address type

        dns_record_id = dns_record["id"]
        dns_record = {
            "name": dns_name,
            "type": ip_address_type,
            "content": ip_address,
            "proxied": proxied_state,
        }
        try:
            dns_record = cf.zones.dns_records.put(
                zone_id, dns_record_id, data=dns_record
            )
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit(
                "/zones.dns_records.put %s - %d %s - api call failed" % (dns_name, e, e)
            )
        print("UPDATED: %s %s -> %s" % (dns_name, old_ip_address, ip_address))
        updated = True

    if updated:
        return

    # no exsiting dns record to update - so create dns record
    dns_record = {"name": dns_name, "type": ip_address_type, "content": ip_address}
    try:
        dns_record = cf.zones.dns_records.post(zone_id, data=dns_record)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit("/zones.dns_records.post %s - %d %s - api call failed" % (dns_name, e, e))
    print("CREATED: %s %s" % (dns_name, ip_address))


def main():
    """Cloudflare API code - example"""

    env = Env()
    zone_name = env.zoon
    dns_name = env.dns_name

    ip_address, ip_address_type = my_ip_address()

    print("MY IP: %s => %s" % (ip_address, dns_name))

    cf = CloudFlare.CloudFlare(email=env.email, token=env.token)

    # grab the zone identifier
    try:
        params = {"name": zone_name}
        zones = cf.zones.get(params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit("/zones %d %s - api call failed" % (e, e))
    except Exception as e:
        exit("/zones.get - %s - api call failed" % (e))

    if len(zones) == 0:
        exit("/zones.get - %s - zone not found" % (zone_name))

    if len(zones) != 1:
        exit("/zones.get - %s - api call returned %d items" % (zone_name, len(zones)))

    zone = zones[0]

    zone_id = zone["id"]

    do_dns_update(cf, zone_id, dns_name, ip_address, ip_address_type)
    exit(0)


if __name__ == "__main__":
    main()
