import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit, faPlus, faTrash } from "@fortawesome/free-solid-svg-icons";
import "./ZoneList.css";
import "../../styles/ButtonStyles.css";
import { useZoneContext } from "../../context/ZoneContext";

const ZoneList: React.FC = () => {
    const { zones, selectedZoneId, isCreatingZone, creatingZone, selectZone, deleteZone, editingZone } =
        useZoneContext();

    return (
        <div className="side-panel-top">
            <table className="zones-table">
                <thead>
                    <tr>
                        <th>
                            <h3>Zones</h3>
                        </th>
                        <th>
                            <button
                                onClick={() => {
                                    if (!isCreatingZone) {
                                        creatingZone();
                                    }
                                }}
                                className={`button ${isCreatingZone ? "pressed" : ""}`}
                                disabled={isCreatingZone}
                            >
                                <FontAwesomeIcon icon={faPlus} />
                            </button>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {Object.entries(zones).map(([id, zone]) => (
                        <tr
                            key={id}
                            className={`zone-item ${selectedZoneId === id ? "selected" : ""}`}
                            onClick={() => selectZone(id)}
                        >
                            <td className="zone-name">{zone.name}</td>
                            <td className="zone-actions">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        selectZone(id);
                                        editingZone(id);
                                    }}
                                    className="button edit"
                                >
                                    <FontAwesomeIcon icon={faEdit} />
                                </button>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        deleteZone(id);
                                    }}
                                    className="button delete"
                                >
                                    <FontAwesomeIcon icon={faTrash} />
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default ZoneList;
