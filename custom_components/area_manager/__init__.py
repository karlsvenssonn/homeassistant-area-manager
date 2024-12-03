from homeassistant.core import HomeAssistant

async def async_setup(hass: HomeAssistant, config: dict):
    async def change_area(call):
        area_id = call.data.get("area_id")
        device_id = call.data.get("device_id")

        if not area_id or not device_id:
            hass.components.persistent_notification.create(
                "Missing required parameters: area_id or device_id.",
                title="Area Manager Error",
            )
            return

        # Access the device registry
        device_registry = hass.helpers.device_registry.async_get(hass)
        device = device_registry.async_get(device_id)
        
        if device:
            device_registry.async_update_device(device.id, area_id=area_id)
            hass.components.persistent_notification.create(
                f"Device {device_id} moved to area {area_id}.",
                title="Area Manager",
            )
        else:
            hass.components.persistent_notification.create(
                f"Device with ID {device_id} not found.",
                title="Area Manager Error",
            )

    # Register the service
    hass.services.async_register("area_manager", "change_area", change_area)
    return True
