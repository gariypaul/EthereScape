// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ScheduledEvent {
    // Define a struct to hold event details.
    struct Event {
        address creator;
        string name;
        bool isActive;
        string ipfsLink;
        string description;
        string location;   // Human-readable location (e.g., "Lake Thunderbird State Park")
        int256 latitude;   // Latitude in degrees (supports negative values)
        int256 longitude;  // Longitude in degrees (supports negative values)
    }

    // Mapping from event IDs to events.
    mapping(uint256 => Event) public events;
    // Array to store event IDs (for enumeration).
    uint256[] public eventIds;
    // Counter for generating new event IDs.
    uint256 public nextEventId;

    // Event emitted when a new event is created.
    event EventCreated(
        uint256 indexed eventId,
        address indexed creator,
        string name,
        string location,
        int256 latitude,
        int256 longitude
    );

    // Create an event with location and geolocation data.
    function createEvent(
        string memory _name,
        bool _isActive,
        string memory _ipfsLink,
        string memory _description,
        string memory _location,
        int256 _latitude,
        int256 _longitude
    ) public returns (uint256) {
        uint256 eventId = nextEventId;
        events[eventId] = Event({
            creator: msg.sender,
            name: _name,
            isActive: _isActive,
            ipfsLink: _ipfsLink,
            description: _description,
            location: _location,
            latitude: _latitude,
            longitude: _longitude
        });
        eventIds.push(eventId);
        nextEventId++;

        emit EventCreated(eventId, msg.sender, _name, _location, _latitude, _longitude);
        return eventId;
    }

    // Retrieve event details by event ID.
    function getEvent(uint256 eventId) public view returns (
        address,
        string memory,
        bool,
        string memory,
        string memory,
        string memory,
        int256,
        int256
    ) {
        Event storage e = events[eventId];
        return (
            e.creator,
            e.name,
            e.isActive,
            e.ipfsLink,
            e.description,
            e.location,
            e.latitude,
            e.longitude
        );
    }

    // Update the active status of an event (only the creator can update).
    function updateEventStatus(uint256 eventId, bool _isActive) public {
        Event storage e = events[eventId];
        require(e.creator == msg.sender, "You are not the creator of this event.");
        e.isActive = _isActive;
    }

    // Return the total number of events.
    function getEventCount() public view returns (uint256) {
        return eventIds.length;
    }

    // Return all events as an array.
    function getAllEvents() public view returns (Event[] memory) {
        uint256 count = eventIds.length;
        Event[] memory allEvents = new Event[](count);
        for (uint256 i = 0; i < count; i++) {
            allEvents[i] = events[eventIds[i]];
        }
        return allEvents;
    }
}
