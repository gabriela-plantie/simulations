import matplotlib.pyplot as plt
import solara
from matplotlib.figure import Figure
from mesa.visualization.utils import update_counter


def agent_portrayal(agent):
    size = 20
    color = "w"
    rider_size = 50

    if agent.rider_is_idle(agent.model.t):
        size = rider_size
        color = "tab:green"
    if agent.rider_is_going_to_vendor():
        size = rider_size
        color = "tab:cyan"
    if agent.rider_is_going_to_customer():
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
    riders_free = sum([r.rider_is_idle() for r in model.riders])
    # Note: you have to use Matplotlib's OOP API instead of plt.hist
    # because plt.hist is not thread-safe.
    ax.plot([model.t], [riders_free])
    solara.FigureMatplotlib(fig)


def plot_lines(df, cols):
    fig, ax1 = plt.subplots()

    for c in cols[0]:
        ax1.plot(df[c], label=c)
    ax1.tick_params("y", colors="blue")
    ax1.legend(loc="upper left")
    ax2 = ax1.twinx()
    for c in cols[1]:
        ax2.plot(df[c], label=c, linestyle="--")
    ax2.tick_params("y", colors="red")
    ax2.legend(loc="upper right")

    plt.show()
