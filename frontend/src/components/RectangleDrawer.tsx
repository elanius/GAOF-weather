import L, { latLngBounds, LatLngBounds } from "leaflet";
import { useMapEvents } from "react-leaflet";

// RectangleDrawer Component
const RectangleDrawer: React.FC<{ onBoundsChange: (bounds: LatLngBounds) => void }> = ({ onBoundsChange }) => {
    const map = useMapEvents({
        mousedown(e) {
            const start = e.latlng;

            // Disable map interactions
            map.dragging.disable();
            map.doubleClickZoom.disable();
            map.scrollWheelZoom.disable();
            map.boxZoom.disable();
            map.keyboard.disable();

            // Create a temporary rectangle and listen for mousemove
            const tempRect = L.rectangle(latLngBounds(start, start), { color: "blue", weight: 2 }).addTo(map);

            const moveHandler = (moveEvent: L.LeafletMouseEvent) => {
                const bounds = latLngBounds(start, moveEvent.latlng);
                tempRect.setBounds(bounds);
            };

            const upHandler = () => {
                // Save final bounds and clean up event listeners
                onBoundsChange(tempRect.getBounds());

                // Remove the temporary rectangle
                map.removeLayer(tempRect);

                // Re-enable map interactions
                map.dragging.enable();
                map.doubleClickZoom.enable();
                map.scrollWheelZoom.enable();
                map.boxZoom.enable();
                map.keyboard.enable();

                // Clean up event listeners
                map.off("mousemove", moveHandler);
                map.off("mouseup", upHandler);
            };

            map.on("mousemove", moveHandler);
            map.on("mouseup", upHandler);
        },
    });

    return null;
};

export default RectangleDrawer;
