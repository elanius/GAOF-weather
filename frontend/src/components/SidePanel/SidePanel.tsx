import React from "react";
import ZoneList from "../ZoneList/ZoneList";
import ZoneProperties from "../ZoneProperties/ZoneProperties";
import "./SidePanel.css";

const SidePanel: React.FC = () => {
    return (
        <div className="side-panel">
            <ZoneList />
            <ZoneProperties />
        </div>
    );
};

export default SidePanel;
