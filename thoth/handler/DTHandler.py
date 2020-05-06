import pandas as pd
import streamlit as st
from sklearn.tree import DecisionTreeClassifier, export_graphviz

import thoth.helper as helper
from thoth import SEED
from thoth.handler.BaseHandler import BaseHandler


class DTHandler(BaseHandler):
    """Page handler for the Decision Tree article (short name 'dt')
    """

    def __init__(self):
        super().__init__("dt")
        self.data_options = ["Breast Cancer", "Iris", "Wine"]
        self.summary = pd.DataFrame(
            {
                "Attribute": ["Power", "Interpretability", "Simplicity"],
                "Score": [3, 5, 4],
            },
        )

    def render_eda(self, index=0):
        return super().render_eda(index=self.data_options.index("Iris"))

    def render_playground(self):
        st.header("Model Playground")
        st.subheader("Parameter Selection")
        params = {"random_state": SEED}
        params["criterion"] = st.selectbox("Criterion", ["gini", "entropy"])
        params["max_depth"] = st.slider("Max Depth", min_value=1, max_value=20, value=5)
        params["min_impurity_decrease"] = st.slider(
            "Min Impurity Decrease",
            min_value=0.0,
            max_value=0.5,
            step=0.001,
            format="%.3f",
        )

        if st.checkbox("Show advanced options"):
            params["splitter"] = st.selectbox("Splitter", ["best", "random"])
            if st.checkbox("Balance classes"):
                params["class_weight"] = "balanced"
            params["min_samples_split"] = st.slider(
                "Min Samples per Split", min_value=0.01, max_value=1.0, step=0.01
            )
            params["max_features"] = st.slider(
                "Number of Features to Consider at Each Split",
                min_value=1,
                max_value=len(self.dataset["feature_names"]),
                value=len(self.dataset["feature_names"]),
            )

        dt = helper.train_model(
            DecisionTreeClassifier, params, self.train_x, self.train_y
        )
        train_metrics = helper.get_metrics(dt, self.train_x, self.train_y).rename(
            index={0: "Train"}
        )
        test_metrics = helper.get_metrics(dt, self.test_x, self.test_y).rename(
            index={0: "Test"}
        )
        st.subheader("Performance Metrics")
        st.write(train_metrics.append(test_metrics))

        st.subheader("View Tree")
        with st.spinner("Plotting tree"):
            tree_dot = export_graphviz(
                dt,
                out_file=None,
                rounded=True,
                filled=True,
                class_names=self.dataset["target_names"],
                feature_names=self.dataset["feature_names"],
            )
            st.graphviz_chart(tree_dot, use_container_width=True)

        st.subheader("Tree Parameters")
        st.write(dt.get_params())
