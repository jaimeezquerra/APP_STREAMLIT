import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("airbnb.csv")

## 1) App setup
st.title('JAIME EZQUERRA DURÁN')

## 2) Sidebar with filters

# Replace NaN values in specific columns with 'Unknown'
df['neighbourhood_group'] = df['neighbourhood_group'].fillna('Unknown')
df['room_type'] = df['room_type'].fillna('Unknown')

# Sidebar filters for selecting neighborhood and room type
neighborhood_group = st.sidebar.selectbox(
    "🏡 **Select Neighborhood Group**",
    df['neighbourhood_group'].unique(),
    key="neighborhood_group_selectbox"
)

room_type = st.sidebar.selectbox(
    "🛏️ **Select Room Type**",
    df['room_type'].unique(),
    key="room_type_selectbox"
)

# Filter the dataframe based on the selections
filtered_df = df[
    (df['neighbourhood_group'] == neighborhood_group) &
    (df['room_type'] == room_type)
]

st.write(f"🔍 **Showing data for {room_type} in {neighborhood_group}**")

## 3) Tabs for different views

# Create two tabs: Insights and Price Recommendation
tab1, tab2 = st.tabs(["📈 Insights", "💰 Price Recommendation"])

# 1. Insights Tab
with tab1:
    st.header("📊 **Insights**")

    # Graph to Study the Relationship Between Listing Type and Number of People
    fig = px.scatter(filtered_df, x="room_type", y="calculated_host_listings_count", title="Room Type vs. Number of Listings")
    st.plotly_chart(fig)

    # Apartments with the Highest Number of Reviews per Month:
    top_reviews = filtered_df[['name', 'neighbourhood', 'reviews_per_month']].sort_values(by='reviews_per_month', ascending=False).head(10)
    fig = px.bar(top_reviews, x='name', y='reviews_per_month', color='neighbourhood', title="Top 10 Apartments by Reviews per Month")
    st.plotly_chart(fig)

    # Relationship Between Reviews and Price:
    fig = px.scatter(filtered_df, x="number_of_reviews", y="price", title="Reviews vs. Price")
    st.plotly_chart(fig)

    # Price Distribution by Listing Type (excluding 'Unknown')
    st.subheader("💲 Price Distribution by Listing Type")
    filtered_box_df = df[df['room_type'] != 'Unknown']  # Exclude 'Unknown' room types
    fig = px.box(filtered_box_df, x="room_type", y="price", title="Price by Listing Type", color="room_type")
    st.plotly_chart(fig)

# 2. Price Recommendation Tab
with tab2:
    st.header("💵 **Price Recommendation**")

    # Inputs for the user to fill in for price recommendation
    neighborhood_group = st.selectbox("🏡 **Select Neighborhood Group**", df['neighbourhood_group'].unique(), key="sim_neighborhood_group")
    room_type = st.selectbox("🛏️ **Select Room Type**", df['room_type'].unique(), key="sim_room_type")

    # New slider for the number of reviews
    num_reviews = st.slider("📝 **Select Number of Reviews Range**", 
                            min_value=int(df['number_of_reviews'].min()), 
                            max_value=int(df['number_of_reviews'].max()), 
                            value=(0, int(df['number_of_reviews'].max())),
                            key="sim_num_reviews")

    # Filter data based on user input
    filtered_df = df[
        (df['neighbourhood_group'] == neighborhood_group) & 
        (df['room_type'] == room_type) &
        (df['number_of_reviews'] >= num_reviews[0]) & 
        (df['number_of_reviews'] <= num_reviews[1])
    ]

    # Check if there are any listings that match the selected options
    if not filtered_df.empty:
        # Calculate the price range using quartiles (IQR method)
        Q1 = filtered_df['price'].quantile(0.25)
        Q3 = filtered_df['price'].quantile(0.75)
        IQR = Q3 - Q1

        # Define a narrower price range based on quartiles
        min_price = Q1 - 1.5 * IQR  # Lower bound of price range (1.5 * IQR below Q1)
        max_price = Q3 + 1.5 * IQR  # Upper bound of price range (1.5 * IQR above Q3)

        # Ensure the price range is within reasonable limits (e.g., no negative prices)
        min_price = max(min_price, 0)

        st.write(f"💡 **Suggested price range for {room_type} in {neighborhood_group} with {num_reviews[0]} - {num_reviews[1]} reviews:**")
        st.markdown(f"**€{min_price:.2f} - €{max_price:.2f}**", unsafe_allow_html=True)
    else:
        st.write(f"❌ **No listings found for {room_type} in {neighborhood_group} with {num_reviews[0]} - {num_reviews[1]} reviews. Please try different options.**")
