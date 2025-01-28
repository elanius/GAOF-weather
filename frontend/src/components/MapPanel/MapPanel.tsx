import React, { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Rectangle } from "react-leaflet";
import L, { latLngBounds, Map } from "leaflet";
import { useZoneContext } from "../../context/ZoneContext";
import "leaflet/dist/leaflet.css";
import "./MapPanel.css";

const MapPanel: React.FC = () => {
    const { zones, selectedZoneId, isCreatingZone, addNewZone, selectZone } = useZoneContext();
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
                    pathOptions={{
                        color: selectedZoneId === id ? "red" : "blue",
                        weight: 2,
                    }}
                    eventHandlers={{
                        click: () => selectZone(id),
                    }}
                />
            ))}
        </MapContainer>
    );
};

export default MapPanel;
