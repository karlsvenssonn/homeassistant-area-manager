import logging
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr, entity_registry as er, area_registry as ar
from homeassistant.components.persistent_notification import async_create as pn_async_create

DOMAIN = "area_manager"
_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema({
    vol.Required("area_name"): str,
    vol.Required("entity_id"): str,
})

async def async_setup(hass: HomeAssistant, config: dict):
    async def notify(msg: str, title: str = "Area Manager"):
        try:
            await pn_async_create(hass, msg, title=title)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Failed to create persistent notification", exc_info=True)

    async def change_area(call: ServiceCall):
        try:
            area_name: str = call.data["area_name"]
            entity_id: str = call.data["entity_id"]

            area_reg = ar.async_get(hass)
            ent_reg = er.async_get(hass)
            dev_reg = dr.async_get(hass)

            area = area_reg.async_get_area_by_name(area_name)
            if not area:
                await notify(f"Area '{area_name}' not found.", "Area Manager Error")
                return

            ent = ent_reg.async_get(entity_id)
            if not ent:
                await notify(f"Entity '{entity_id}' not found.", "Area Manager Error")
                return

            # Prefer moving the device; fallback to entity
            if ent.device_id:
                dev = dev_reg.async_get(ent.device_id)
                if dev:
                    dev_reg.async_update_device(dev.id, area_id=area.id)
                    await notify(f"Device for '{entity_id}' moved to area '{area_name}'.")
                    return

            ent_reg.async_update_entity(entity_id, area_id=area.id)
            await notify(f"Entity '{entity_id}' moved to area '{area_name}'.")

        except Exception as e:  # noqa: BLE001
            _LOGGER.exception("area_manager.change_area failed: %s", e)
            await notify(f"Unexpected error: {e}", "Area Manager Error")
            return

    hass.services.async_register(DOMAIN, "change_area", change_area, schema=SERVICE_SCHEMA)
    return True