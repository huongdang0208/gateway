query_devices_by_license = """
query Devices_by_license($license: String!) {
  devices_by_license(license: $license) {
    items {
      current_state
      created_at
      device_name
      id
      protocol
      pin
      updated_at
      userID
    }
  }
}
"""