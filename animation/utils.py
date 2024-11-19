import solara
from matplotlib.figure import Figure
from mesa.visualization.utils import update_counter

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


@solara.component
def Graph(model):
    update_counter.get()  # This is required to update the counter
    # Note: you must initialize a figure using this method instead of
    # plt.figure(), for thread safety purpose
    fig = Figure()
    ax = fig.subplots()
    riders_free = sum([r.state == RiderStatus.RIDER_FREE for r in model.riders])
    # Note: you have to use Matplotlib's OOP API instead of plt.hist
    # because plt.hist is not thread-safe.
    ax.plot([model.t], [riders_free])
    solara.FigureMatplotlib(fig)
