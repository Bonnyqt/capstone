
    const canvas = document.getElementById('canvas');
    const svgCanvas = document.getElementById('svgCanvas');
    const addNodeBtn = document.getElementById('addNodeBtn');
    const clearBtn = document.getElementById('clearBtn');
    const addWireBtn = document.getElementById('addWireBtn');
    const demoBtn = document.getElementById('demoBtn');
    const iconModal = document.getElementById('iconModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const iconList = document.getElementById('iconList');
    const nodeConfigModal = document.getElementById('nodeConfigModal');
    const closeNodeConfigModalBtn = document.getElementById('closeNodeConfigModalBtn');
    const ipAddressInput = document.getElementById('ipAddressInput');
    const tooltipInput = document.getElementById('tooltipInput');
    const vulnerabilityInput = document.getElementById('vulnerabilityInput');
    const titleInput = document.getElementById('titleInput');
    const saveNodeBtn = document.getElementById('saveNodeBtn');

    let nodeCount = 0;
    let wireStart = null;
    let wires = [];
    let packet = document.createElement('div');
    packet.className = 'packet';
    canvas.appendChild(packet);
    let selectedIconClass = 'fas fa-user'; // Default icon

    addNodeBtn.addEventListener('click', () => {
        // Show the icon selection modal
        iconModal.style.display = 'block';
    });

    // Close modal button for icon selection
    closeModalBtn.addEventListener('click', () => {
        iconModal.style.display = 'none';
    });

    // Icon selection
    iconList.addEventListener('click', (e) => {
        if (e.target.classList.contains('icon')) {
            selectedIconClass = e.target.getAttribute('data-icon');
            nodeConfigModal.style.display = 'block'; // Show node configuration modal
            iconModal.style.display = 'none'; // Close the icon selection modal
        }
    });

    // Close node configuration modal
    closeNodeConfigModalBtn.addEventListener('click', () => {
        nodeConfigModal.style.display = 'none';
    });

    // Save node configuration
    saveNodeBtn.addEventListener('click', () => {
        const ipAddress = ipAddressInput.value;
        const tooltipDescription = tooltipInput.value;
        const vulnerability = vulnerabilityInput.value;
        const title = titleInput.value;

        addNode(selectedIconClass, ipAddress, tooltipDescription, vulnerability, title);
        ipAddressInput.value = ''; // Clear input field
        tooltipInput.value = ''; // Clear input field
        vulnerabilityInput.value = ''; // Clear input field
        titleInput.value = ''; // Clear input field
        nodeConfigModal.style.display = 'none'; // Close the modal
    });

    function addNode(iconClass, ipAddress, tooltipDescription, vulnerability, title) {
        const node = document.createElement('div');
        node.className = 'node';
        node.id = `node-${nodeCount++}`;
        node.style.left = '50px';
        node.style.top = '50px';

        const icon = document.createElement('i');
        icon.className = iconClass;
        node.appendChild(icon);

        const tooltip = document.createElement('div');
tooltip.className = 'tooltip';
tooltip.innerHTML = tooltipDescription || 'Double-click to edit tooltip.';

// Add IP and vulnerability in a row format
const infoRow = document.createElement('div');
infoRow.className = 'info-row';

if (ipAddress) {
    const ipAddressElement = document.createElement('div');
    ipAddressElement.className = 'ip-address';
    ipAddressElement.textContent = `IP: ${ipAddress}`; // Display IP address
    infoRow.appendChild(ipAddressElement);
}

if (vulnerability) {
    const vulnerabilityElement = document.createElement('div');
    vulnerabilityElement.className = 'vulnerability';
    vulnerabilityElement.textContent = `Vuln: ${vulnerability}`; // Display vulnerability
    infoRow.appendChild(vulnerabilityElement);
}

// Append the infoRow to the tooltip
tooltip.appendChild(infoRow);
        node.appendChild(tooltip);
        
        // Create a container for details below the node
        const detailsContainer = document.createElement('div');
        detailsContainer.className = 'details-container';

        if (title) {
            const titleElement = document.createElement('div');
            titleElement.className = 'node-title';
            titleElement.textContent = title; // Display title
            detailsContainer.appendChild(titleElement);
        }

        // Append the details container to the node
        node.appendChild(detailsContainer);

        canvas.appendChild(node);

        // Make the node draggable
        let offsetX, offsetY;

// Make the node draggable
node.addEventListener('mousedown', (e) => {
    // Prevent text selection while dragging
    e.preventDefault();
    
    // Get the position of the mouse relative to the node
    offsetX = e.clientX - node.getBoundingClientRect().left;
    offsetY = e.clientY - node.getBoundingClientRect().top;
    
    node.style.cursor = 'grabbing'; // Change cursor during drag

    const moveNode = (event) => {
        // Calculate the new position based on the cursor's current position
        const newLeft = event.clientX - offsetX;
        const newTop = event.clientY - offsetY;

        // Update the position of the node
        node.style.left = `${newLeft}px`;
        node.style.top = `${newTop}px`;
        updateWires(); // Update wires when the node moves
    };

    const stopMove = () => {
        document.removeEventListener('mousemove', moveNode);
        document.removeEventListener('mouseup', stopMove);
        node.style.cursor = 'grab'; // Reset cursor
    };

    // Add event listeners for mouse movement and mouse up
    document.addEventListener('mousemove', moveNode);
    document.addEventListener('mouseup', stopMove);
});
        // Double-click to edit tooltip
        node.addEventListener('dblclick', () => {
            const newTooltip = prompt('Enter new tooltip:');
            if (newTooltip) {
                tooltip.innerHTML = newTooltip;
            }
        });

        // Create draggable area for the node
        node.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        // Animate adding the node
        node.style.transform = 'scale(0.5)';
        setTimeout(() => {
            node.style.transform = 'scale(1)';
        }, 0);
    }

    function updateWires() {
        svgCanvas.innerHTML = ''; // Clear existing wires
        wires.forEach(wire => {
            const startNode = document.getElementById(wire.start);
            const endNode = document.getElementById(wire.end);
            if (startNode && endNode) {
                const startX = parseInt(startNode.style.left) + 25;
                const startY = parseInt(startNode.style.top) + 25;
                const endX = parseInt(endNode.style.left) + 25;
                const endY = parseInt(endNode.style.top) + 25;

                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', startX);
                line.setAttribute('y1', startY);
                line.setAttribute('x2', endX);
                line.setAttribute('y2', endY);
                line.classList.add('wire');
                svgCanvas.appendChild(line);
            }
        });
    }

    clearBtn.addEventListener('click', () => {
        while (canvas.firstChild) {
            canvas.removeChild(canvas.firstChild);
        }
        wires = [];
        svgCanvas.innerHTML = '';
        nodeCount = 0;
    });

    addWireBtn.addEventListener('click', () => {
        const nodes = document.querySelectorAll('.node');
        if (nodes.length < 2) {
            alert('Add at least two nodes to connect with a wire.');
            return;
        }
    
        if (wireStart === null) {
            wireStart = null; // Reset wire start
            nodes.forEach(node => {
                node.style.cursor = 'pointer'; // Change cursor to pointer
                node.onclick = () => {
                    if (!wireStart) {
                        wireStart = node; // Set the start node
                        alert(`Selected ${wireStart.id} as the start node. Click another node to connect.`);
                    } else {
                        if (node !== wireStart) {
                            const startX = parseInt(wireStart.style.left) + 25;
                            const startY = parseInt(wireStart.style.top) + 25;
                            const endX = parseInt(node.style.left) + 25;
                            const endY = parseInt(node.style.top) + 25;
    
                            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                            line.setAttribute('x1', startX);
                            line.setAttribute('y1', startY);
                            line.setAttribute('x2', endX);
                            line.setAttribute('y2', endY);
                            line.classList.add('wire'); // Add wire class for animation
                            line.setAttribute('data-start', wireStart.id); // Store start node id
                            line.setAttribute('data-end', node.id); // Store end node id
                            line.setAttribute('data-start-x', startX); // Store start x position
                            line.setAttribute('data-start-y', startY); // Store start y position
                            line.setAttribute('data-end-x', endX); // Store end x position
                            line.setAttribute('data-end-y', endY); // Store end y position
                            svgCanvas.appendChild(line);
    
                            // Store the wire connection along with positions
                            wires.push({
                                start: wireStart.id,
                                end: node.id,
                                startX: startX,
                                startY: startY,
                                endX: endX,
                                endY: endY
                            });
                            wireStart = null; // Reset wire start
                            nodes.forEach(node => {
                                node.style.cursor = 'grab'; // Reset cursor for nodes
                                node.onclick = null; // Reset click event for nodes
                            });
                        } else {
                            alert('You cannot connect a node to itself.');
                        }
                    }
                };
            });
        }
    });
    
    document.getElementById('saveTitleBtn').addEventListener('click', () => {
        const canvasTitle = document.getElementById('canvasTitleInput').value.trim();
    
        if (!canvasTitle) {
            alert('Please enter a title for the canvas.');
            return;
        }
    
        const nodes = [];
    
        // Collect all node data
        document.querySelectorAll('.node').forEach(node => {
            const nodeData = {
                id: node.id,
                iconClass: node.querySelector('i')?.className || '',
                left: node.style.left || '',
                top: node.style.top || '',
                ipAddress: node.querySelector('.ip-address')?.textContent || '',
                vulnerability: node.querySelector('.vulnerability')?.textContent || '',
                title: node.querySelector('.node-title')?.textContent || '',
                tooltip: node.querySelector('.tooltip')?.textContent || ''
            };
            // Push only non-empty nodes
            if (nodeData.id && nodeData.title) {
                nodes.push(nodeData);
            }
        });
    
        // Ensure the wires array is properly defined and populated
        let wires = [];
        document.querySelectorAll('.wire').forEach(wire => {
            const startNodeId = wire.getAttribute('data-start');
            const endNodeId = wire.getAttribute('data-end');
            const startNode = document.getElementById(startNodeId);
            const endNode = document.getElementById(endNodeId);
    
            const wireData = {
                start: startNodeId,
                end: endNodeId,
                startX: wire.getAttribute('data-start-x'),
                startY: wire.getAttribute('data-start-y'),
                endX: wire.getAttribute('data-end-x'),
                endY: wire.getAttribute('data-end-y'),
                startTitle: startNode?.querySelector('.node-title')?.textContent || '',  // Add start node title
                endTitle: endNode?.querySelector('.node-title')?.textContent || ''  // Add end node title
            };
            // Push only non-empty wires
            if (wireData.start && wireData.end) {
                wires.push(wireData);
            }
        });
    
        // Prepare the canvas state data
        const canvasState = {
            title: canvasTitle,
            nodes: nodes,
            wires: wires
        };
    
        // Send the state to the server using AJAX/fetch
        fetch('/save_canvas_state/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(canvasState)
        }).then(response => {
            if (response.ok) {
                alert('Canvas state saved successfully!');
                document.getElementById('titleModal').style.display = 'none';
            } else {
                alert('Failed to save canvas state.');
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('An error occurred while saving the canvas state.');
        });
    });
    
    
    
    
    
    // Function to get the CSRF token (used by Django for security)
    function getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    
    
    demoBtn.addEventListener('click', () => {
        const nodes = document.querySelectorAll('.node');
        if (nodes.length < 2) {
            alert('Add at least two nodes to simulate packet transfer.');
            return;
        }
    
        let currentWireIndex = 0;
    
        const animatePacketThroughWires = () => {
            const wire = wires[currentWireIndex];
            const startNode = document.getElementById(wire.start);
            const endNode = document.getElementById(wire.end);
            const startX = parseInt(startNode.style.left) + 25;
            const startY = parseInt(startNode.style.top) + 25;
            const endX = parseInt(endNode.style.left) + 25;
            const endY = parseInt(endNode.style.top) + 25;
    
            // Position the packet at the start node
            packet.style.left = `${startX}px`;
            packet.style.top = `${startY}px`;
            packet.style.display = 'block';
    
            // Show tooltip at the start node
            const tooltip = startNode.querySelector('.tooltip');
            tooltip.style.visibility = 'visible';
            tooltip.style.opacity = 1;
    
            // Pause at the start node for 2 seconds
            setTimeout(() => {
                // Animate the packet movement to the end node
                const distanceX = endX - startX;
                const distanceY = endY - startY;
                const duration = 1000; // 1 second
                const startTime = performance.now();
    
                function animatePacket(timestamp) {
                    const elapsed = timestamp - startTime;
                    const progress = Math.min(elapsed / duration, 1); // Normalize progress
    
                    const easing = (t) => t * (2 - t); // Ease out effect
                    const easedProgress = easing(progress);
    
                    packet.style.left = `${startX + distanceX * easedProgress}px`;
                    packet.style.top = `${startY + distanceY * easedProgress}px`;
    
                    if (progress < 1) {
                        requestAnimationFrame(animatePacket);
                    } else {
                        packet.style.display = 'none'; // Hide the packet after animation
    
                        // Hide the tooltip after reaching the end node
                        tooltip.style.visibility = 'hidden';
                        tooltip.style.opacity = 0;
    
                        currentWireIndex++; // Move to the next wire
    
                        // Check if there are more wires to animate
                        if (currentWireIndex < wires.length) {
                            animatePacketThroughWires(); // Animate the next wire
                        }
                    }
                }
    
                requestAnimationFrame(animatePacket);
            }, 2000); // Pause for 2 seconds before moving to the end node
        };
    
        // Start animation at the initial node
        animatePacketThroughWires();
    });
    
    


