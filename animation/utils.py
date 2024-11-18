from agents.riders import RiderStatus


def agent_portrayal(agent):
    size = 20
    color = "w"
    rider_size = 50

    if agent.state == RiderStatus.RIDER_FREE:
        size = rider_size
        color = "tab:green"
    if agent.state == RiderStatus.RIDER_GOING_TO_VENDOR:
        size = rider_size
        color = "tab:cyan"
    if agent.state == RiderStatus.RIDER_GOING_TO_CUSTOMER:
        size = rider_size
        color = "tab:blue"

    return {"size": size, "color": color, "label": agent.pos}
