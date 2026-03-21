import { useState } from "react";

function TreeNode({ name, node, depth, onFileClick, currentPath }) {
    const [open, setOpen] = useState(false);
    const isFolder = typeof node === "object";

    const fullPath = currentPath ? `${currentPath}/${name}` : name;

    return (
        <div style={{ marginLeft: depth * 14 }}>
            <div
                style={{
                    cursor: "pointer",
                    padding: "2px 6px"
                }}
                onClick={() => {
                    if (isFolder) {
                        setOpen(!open);
                    } else {
                        onFileClick(fullPath);
                    }
                }}
            >
                {isFolder ? (open ? "▼" : "▶") : "🗎"} {name}
            </div>

            {isFolder && open &&
                Object.entries(node).map(([key, value]) => (
                    <TreeNode
                        key={key}
                        name={key}
                        node={value}
                        depth={depth + 1}
                        onFileClick={onFileClick}
                        currentPath={fullPath}
                    />
                ))
            }
        </div>
    );
}

export default function RepoTree({ data, onFileClick }) {
    return (
        <div className="tree-container">
            <h3>
                Repository Structure ({data.total_files} files)
            </h3>

            {Object.entries(data.tree).map(([key, value]) => (
                <TreeNode
                    key={key}
                    name={key}
                    node={value}
                    depth={0}
                    onFileClick={onFileClick}
                    currentPath=""
                />
            ))}
        </div>
    );
}