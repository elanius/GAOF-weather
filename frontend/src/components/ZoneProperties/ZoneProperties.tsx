import React, { useState, useEffect } from "react";
import "./ZoneProperties.css";
import "../../styles/ButtonStyles.css";
import { useZoneContext, ZoneType } from "../../context/ZoneContext";

const ZoneProperties: React.FC = () => {
    const { selectedZoneId, editZone, deleteZone, selectedZone } = useZoneContext();
    const zone = selectedZone();
    const [newZoneName, setNewZoneName] = useState<string>(zone ? zone.name : "");
    const [zoneType, setZoneType] = useState<string>(zone ? zone.type : "");

    useEffect(() => {
        console.log("Updated selectedZoneId:", selectedZoneId);
        if (zone) {
            setNewZoneName(zone.name);
            setZoneType(zone.type);
        }
    }, [zone, selectedZoneId]);

    const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setNewZoneName(e.target.value);
    };

    const handleZoneTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setZoneType(e.target.value);
    };

    const handleSave = () => {
        console.log("Selected Zone ID:", selectedZoneId);
        editZone(selectedZoneId!, newZoneName, zoneType as ZoneType);
    };

    const handleCancel = () => {
        if (zone) {
            if (zone.isCreating) {
                deleteZone(selectedZoneId!);
            } else if (zone.isEditing) {
                zone.isEditing = false;
                setNewZoneName(zone.name);
                setZoneType(zone.type);
            }
        }
    };

    if (zone !== null) {
        return (
            <div className="side-panel-bottom">
                <table className="property-table">
                    <thead>
                        <tr>
                            <th colSpan={2}>
                                <h3>Zone properties</h3>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td className="property-name">Name</td>
                            <td className="property-value">
                                <input
                                    type="text"
                                    value={newZoneName}
                                    onChange={handleNameChange}
                                    disabled={!zone.isEditing}
                                />
                            </td>
                        </tr>
                        <tr>
                            <td className="property-name">Type</td>
                            <td className="property-value">
                                <select value={zoneType} onChange={handleZoneTypeChange} disabled={!zone.isEditing}>
                                    {Object.values(ZoneType).map((type) => (
                                        <option key={type} value={type}>
                                            {type}
                                        </option>
                                    ))}
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td className="property-name">SW Corner Latitude</td>
                            <td className="property-value">{zone.bounds.getSouthWest().lat}</td>
                        </tr>
                        <tr>
                            <td className="property-name">SW Corner Longitude</td>
                            <td className="property-value">{zone.bounds.getSouthWest().lng}</td>
                        </tr>
                        <tr>
                            <td className="property-name">NE Corner Latitude</td>
                            <td className="property-value">{zone.bounds.getNorthEast().lat}</td>
                        </tr>
                        <tr>
                            <td className="property-name">NE Corner Longitude</td>
                            <td className="property-value">{zone.bounds.getNorthEast().lng}</td>
                        </tr>
                        {zone.isEditing && (
                            <tr>
                                <td colSpan={2} className="property-value">
                                    <button onClick={handleSave} className="button accept">
                                        {zone.isCreating ? "Create" : "Save"}
                                    </button>
                                    <button onClick={handleCancel} className="button delete">
                                        Cancel
                                    </button>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        );
    }

    return <></>;
};

export default ZoneProperties;
