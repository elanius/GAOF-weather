import React, { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Rectangle } from "react-leaflet";
import L, { latLngBounds, Map } from "leaflet";
import { useZoneContext, Zone } from "../../context/ZoneContext";
import "leaflet/dist/leaflet.css";
import "./MapPanel.css";

const getZoneColor = (zone: Zone, selectedZoneId: string) => {
    if (selectedZoneId === zone.id) {
        return {
            color: "red",
            weight: 2,
        };
    }

    if (zone.active == false) {
        return {
            color: "gray",
            weight: 2,
        };
    }

    if (zone.type == "auto_group") {
        return {
            color: "#1fe053",
            weight: 2,
            fillColor: "none",
        };
    }

    return {
        color: "blue",
        weight: 2,
    };
};

const MapPanel: React.FC = () => {
    const { zones, selectedZoneId, isCreatingZone, isLocalizingZone, addNewZone, selectZone, localizeZone } =
        useZoneContext();
    const mapRef = useRef<Map | null>(null);
    const [waitForAccept, setWaitForAccept] = useState(false);

    useEffect(() => {
        console.log("map - isCreatingZone: ", isCreatingZone);
        if (!mapRef.current) return;
        const map = mapRef.current;

        if (isCreatingZone) {
            map.dragging.disable();
            map.doubleClickZoom.disable();
            map.scrollWheelZoom.disable();
        } else {
            map.dragging.enable();
            map.doubleClickZoom.enable();
            map.scrollWheelZoom.enable();
            setWaitForAccept(false);
        }

        const handleMouseDown = (e: L.LeafletMouseEvent) => {
            if (!isCreatingZone || waitForAccept) return;

            const start = e.latlng;
            const tempRect = L.rectangle(latLngBounds(start, start), { color: "blue", weight: 2 }).addTo(map);

            const moveHandler = (moveEvent: L.LeafletMouseEvent) => {
                const bounds = latLngBounds(start, moveEvent.latlng);
                tempRect.setBounds(bounds);
            };

            const upHandler = () => {
                const finalBounds = tempRect.getBounds();
                addNewZone(finalBounds);
                setWaitForAccept(true);
                map.off("mousemove", moveHandler);
                map.off("mouseup", upHandler);
                map.removeLayer(tempRect);
            };

            map.on("mousemove", moveHandler);
            map.on("mouseup", upHandler);
        };

        map.on("mousedown", handleMouseDown);

        return () => {
            map.off("mousedown", handleMouseDown);
            map.dragging.enable();
            map.doubleClickZoom.enable();
            map.scrollWheelZoom.enable();
        };
    }, [isCreatingZone, addNewZone, waitForAccept]);

    useEffect(() => {
        if (!mapRef.current || !selectedZoneId || !isLocalizingZone) return;
        const map = mapRef.current;
        const zone = zones[selectedZoneId];
        if (zone) {
            const bounds = zone.bounds;
            map.fitBounds(bounds, { padding: [200, 200] }); // Add padding to zoom out a little bit
        }
        localizeZone(selectedZoneId, false);
    }, [selectedZoneId, zones, isLocalizingZone]);

    return (
        <MapContainer
            center={[51.505, -0.09]}
            zoom={13}
            style={{ height: "100%", width: "100%" }}
            ref={(mapInstance) => {
                if (mapInstance) {
                    mapRef.current = mapInstance as unknown as Map;
                }
            }}
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {Object.entries(zones).map(([id, zone]) => (
                <Rectangle
                    key={id}
                    bounds={zone.bounds}
                    pathOptions={getZoneColor(zone, selectedZoneId || "")}
                    eventHandlers={{
                        click: () => selectZone(id),
                    }}
                />
            ))}
        </MapContainer>
    );
};

export default MapPanel;
