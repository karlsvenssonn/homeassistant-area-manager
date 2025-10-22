from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.area_registry import async_get as async_get_area_registry

DOMAIN = "area_manager"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Area Manager component."""

    async def change_area(call: ServiceCall):
        """Handle the change_area service call."""
        area_name = call.data.get("area_name")
        entity_id = call.data.get("entity_id")

        # Validate input parameters
        if not area_name or not entity_id:
            hass.components.persistent_notification.create(
                "Missing required parameters: area_name or entity_id.",
                title="Area Manager Error",
            )
            return

        # Access the area registry to fetch the area_id
        area_registry = async_get_area_registry(hass)
        area = next((a for a in area_registry.async_list_areas() if a.name == area_name), None)

        if not area:
            hass.components.persistent_notification.create(
                f"Area with name {area_name} not found.",
                title="Area Manager Error",
            )
            return

        area_id = area.id

        # Access the entity registry to fetch the device_id
        entity_registry = async_get_entity_registry(hass)
        entity_entry = entity_registry.async_get(entity_id)

        if not entity_entry:
            hass.components.persistent_notification.create(
                f"Entity with ID {entity_id} not found.",
                title="Area Manager Error",
            )
            return

        # Get the device ID from the entity entry
        device_id = entity_entry.device_id
        if not device_id:
            hass.components.persistent_notification.create(
                f"Entity {entity_id} is not linked to a device.",
                title="Area Manager Error",
            )
            return

        # Access the device registry
        device_registry = async_get_device_registry(hass)
        device = device_registry.async_get(device_id)

        if device:
            # Update the device's area
            device_registry.async_update_device(device.id, area_id=area_id)
            hass.components.persistent_notification.create(
                f"Device linked to entity {entity_id} moved to area {area_name}.",
                title="Area Manager",
            )
        else:
            hass.components.persistent_notification.create(
                f"Device linked to entity {entity_id} not found.",
                title="Area Manager Error",
            )

    # Register the service
    hass.services.async_register(DOMAIN, "change_area", change_area)

    return True