import React, { useState } from "react";
import { MapContainer, Marker, Popup, Rectangle, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { LatLngBounds } from "leaflet";
import RectangleDrawer from "./components/RectangleDrawer";

// Main App Component
const App: React.FC = () => {
    const [rectBounds, setRectBounds] = useState<LatLngBounds | null>(null);
    const [drawingMode, setDrawingMode] = useState(false);

    return (
        <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
            {/* Side Panel */}
            <div
                style={{
                    width: "300px",
                    background: "#f7f7f7",
                    borderRight: "1px solid #ddd",
                    padding: "20px",
                    boxSizing: "border-box",
                }}
            >
                <h3>Zone Management</h3>
                <button
                    onClick={() => setDrawingMode(!drawingMode)}
                    style={{
                        padding: "10px 20px",
                        background: drawingMode ? "red" : "green",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                    }}
                >
                    {drawingMode ? "Stop Drawing" : "Create Zone"}
                </button>
                <div style={{ marginTop: "20px" }}>
                    <h4>Zone Coordinates</h4>
                    {rectBounds ? (
                        <pre
                            style={{
                                background: "#eee",
                                padding: "10px",
                                borderRadius: "4px",
                                overflowX: "auto",
                                maxHeight: "400px",
                            }}
                        >
                            {JSON.stringify(
                                {
                                    southwest: rectBounds.getSouthWest(),
                                    northeast: rectBounds.getNorthEast(),
                                    northwest: rectBounds.getNorthWest(),
                                    southeast: rectBounds.getSouthEast(),
                                },
                                null,
                                2
                            )}
                        </pre>
                    ) : (
                        <p>No zone created yet.</p>
                    )}
                </div>
            </div>

            {/* Map Container */}
            <div style={{ flex: 1 }}>
                <MapContainer
                    center={[51.505, -0.09]}
                    zoom={13}
                    scrollWheelZoom={true}
                    style={{ height: "100%", width: "100%" }}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    <Marker position={[51.505, -0.09]}>
                        <Popup>
                            A pretty CSS3 popup. <br /> Easily customizable.
                        </Popup>
                    </Marker>

                    {/* Enable RectangleDrawer only when drawingMode is active */}
                    {drawingMode && <RectangleDrawer onBoundsChange={setRectBounds} />}

                    {/* Render the rectangle on the map if bounds are set */}
                    {rectBounds && <Rectangle bounds={rectBounds} pathOptions={{ color: "red", weight: 2 }} />}
                </MapContainer>
            </div>
        </div>
    );
};

export default App;
