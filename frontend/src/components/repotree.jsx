import { useState } from "react";

function TreeNode({ name, node, depth }) {
    const [open, setOpen] = useState(false);
    const isFolder = typeof node === "object";

    return (
        <div style={{ marginLeft: depth * 14 }}>
            <div
                style={{ cursor: isFolder ? "pointer" : "default" }}
                onClick={() => isFolder && setOpen(!open)}
            >
                {isFolder ? (open ? "📂" : "📁") : "📄"} {name}
            </div>

            {isFolder && open &&
                Object.entries(node).map(([key, value]) => (
                    <TreeNode
                        key={key}
                        name={key}
                        node={value}
                        depth={depth + 1}
                    />
                ))
            }
        </div>
    );
}

export default function RepoTree({ data }) {
    return (
        <div>
            <h3>Repository Structure ({data.total_files} files, {data.total_folders} folders)</h3>
            {Object.entries(data.tree).map(([key, value]) => (
                <TreeNode key={key} name={key} node={value} depth={0} />
            ))}
        </div>
    );
}