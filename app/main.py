from os.path import dirname, join
import random
import string

import pandas as pd
from sklearn.datasets import make_blobs

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    Button,
    ColumnDataSource,
    CustomJS,
    DataTable,
    TableColumn,
)
from bokeh.plotting import figure

# Make some dummy data
# X is shape (n_samples, n_features)
coords, y = make_blobs(n_samples=400, n_features=2, centers=4)

# Make dataframe with coordinates
df = pd.DataFrame(coords, columns=["x", "y"])
# Add a random text label field to dataframe
df["label"] = [
    "".join(random.choice(string.ascii_lowercase) for i in range(4)) for j in range(400)
]

# Set this dataframe as source1
source1 = ColumnDataSource(data=df)

# Scatterplot tied to source1
scatter = figure(
    plot_width=600, plot_height=600, tools="pan,box_zoom,box_select,lasso_select,reset"
)
scatter.circle(
    "x",
    "y",
    size=2,
    source=source1,
    selection_color="orange",
    alpha=0.6,
    nonselection_alpha=0.1,
    selection_alpha=0.4,
)

# Table tied to source2 (by default filled with all values)
source2 = ColumnDataSource(data=df)
columns = [
    TableColumn(field="x", title="x_coord"),
    TableColumn(field="y", title="y_coord"),
    TableColumn(field="label", title="some_label"),
]
data_table = DataTable(source=source2, columns=columns, width=600, height=600)


# JavaScript to send the selection on source1 to source2 (the table)
# The key piece is the cb_obj.indices, which I don't really understand
source1.selected.js_on_change(
    "indices",
    CustomJS(
        args=dict(source1=source1, source2=source2),
        code="""
        var inds = cb_obj.indices;
        var d1 = source1.data;
        var d2 = source2.data;
        d2['x'] = []
        d2['y'] = []
        d2['label'] = []
        for (var i = 0; i < inds.length; i++) {
            d2['x'].push(d1['x'][inds[i]])
            d2['y'].push(d1['y'][inds[i]])
            d2['label'].push(d1['label'][inds[i]])
        }
        source2.change.emit();
        data_table.change.emit();
""",
    ),
)

# Save button with custom JS download functionality
button = Button(label="Download", button_type="success")
button.js_on_click(
    CustomJS(
        args=dict(source=source2),
        code=open(join(dirname(__file__), "download.js")).read(),
    )
)

# Layout
curdoc().add_root(row(scatter, column(data_table, button)))
curdoc().title = "Scatter linked to table with download"
