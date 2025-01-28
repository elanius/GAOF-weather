import React from "react";
import MapPanel from "./components/MapPanel/MapPanel";
import SidePanel from "./components/SidePanel/SidePanel";
import { ZoneProvider } from "./context/ZoneContext";
import "./App.css";

const App: React.FC = () => {
    return (
        <div className="app-container">
            <ZoneProvider>
                <MapPanel />
                <SidePanel />
            </ZoneProvider>
        </div>
    );
};

export default App;
