import re
import string
import matplotlib.pyplot as plt
import seaborn as sns

def standardise_column_names(df, remove_punct=True):
    """ Converts all DataFrame column names to lower case replacing
    whitespace of any length with a single underscore. Can also strip
    all punctuation from column names.
    
    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame with non-standardised column names.
    remove_punct: bool (default True)
        If True will remove all punctuation from column names.
    
    Returns
    -------
    df: pandas.DataFrame
        DataFrame with standardised column names.
    Example
    -------
    >>> df = pd.DataFrame({'Column With Spaces': [1,2,3,4,5],
                           'Column-With-Hyphens&Others/': [6,7,8,9,10],
                           'Too    Many Spaces': [11,12,13,14,15],
                           })
    >>> df = standardise_column_names(df)
    >>> print(df.columns)
    Index(['column_with_spaces',
           'column_with_hyphens_others',
           'too_many_spaces'], dtype='object')
    """
    
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))

    for c in df.columns:
        c_mod = c.lower()
        if remove_punct:            
            c_mod = c_mod.translate(translator)
        c_mod = '_'.join(c_mod.split(' '))
        if c_mod[-1] == '_':
            c_mod = c_mod[:-1]
        c_mod = re.sub(r'\_+', '_', c_mod)
        df.rename({c: c_mod}, inplace=True, axis=1)
    return df



def plot_boxplots(data, columns):
    n = len(columns)
    num_rows = (n + 1) // 2  # Calculate the number of subplot rows

    # Generate a color palette with n unique colors
    colors = sns.color_palette('icefire', n)

    fig, axes = plt.subplots(num_rows, 2, figsize=(12, 4*num_rows))
    axes = axes.flatten()  # Flatten the axes array for easy indexing

    # Loop through the columns and create box plots with unique colors
    for i, (column, color) in enumerate(zip(columns, colors)):

        # mean annotation
        mean_val = data[column].mean()
        median_val = data[column].median()

        axes[i].axvline(mean_val, color='black', linestyle='--', label=f'Mean = {mean_val:.2f}')
        axes[i].axvline(median_val, color='green', linestyle='--', label=f'Median = {median_val:.2f}')
        ax = axes[i]
        sns.boxplot(data=data[column], ax=ax, color=color, orient='horizontal')
        ax.set_title(column)
        axes[i].legend()

    # Remove any empty subplots
    for j in range(n, len(axes)):
        fig.delaxes(axes[j])

    
    plt.legend()
    plt.tight_layout()
    plt.show()


def distribution_plot(data, include_columns=None, exclude_columns=None, title='Distribution Plot'):
    num_features = data.select_dtypes(include='number').columns.tolist()
    cat_features = data.select_dtypes(include='object').columns.tolist()

    if include_columns:
        num_features = list(set(num_features) & set(include_columns))
        cat_features = list(set(cat_features) & set(include_columns))
    elif exclude_columns:
        num_features = list(set(num_features) - set(exclude_columns))
        cat_features = list(set(cat_features) - set(exclude_columns))

    num_subplot_rows = (len(num_features) + 2) // 3
    cat_subplot_rows = (len(cat_features) + 2) // 3

    fig, axes = plt.subplots(nrows=num_subplot_rows + cat_subplot_rows, ncols=3, figsize=(20, 5 * (num_subplot_rows + cat_subplot_rows)))
    axes = axes.flatten()
    for i, column in enumerate(num_features):
        mean_val = data[column].mean()
        median_val = data[column].median()

        axes[i].axvline(mean_val, color='black', linestyle='--', label=f'Mean = {mean_val:.2f}')
        axes[i].axvline(median_val, color='green', linestyle='--', label=f'Median = {median_val:.2f}')

        axes[i].legend()
        sns.histplot(data=data, x=column, ax=axes[i], kde=True, color='orange')
        axes[i].set_title(column, fontfamily='serif')

    for j, column in enumerate(cat_features, start=i + 1 if any(num_features) else 0):
        sns.countplot(data=data, x=column, ax=axes[j], order=data[column].value_counts().index.sort_values())
        axes[j].set_title(column, fontfamily='serif')

    n = len(num_features) + len(cat_features)
    for k in range(n, len(axes)):
        fig.delaxes(axes[k])

    fig.suptitle(title)
    fig.tight_layout()
    plt.show()

import seaborn as sns
import matplotlib.pyplot as plt

def plot_norm_countplot(data, category_col, hue_col=None, horizontal=False, title=None, xticks_rotation=45, **kwargs):

    # Calculate the count and percentage for each category and hue
    if hue_col is None:
        counts = data[category_col].value_counts(normalize=True).mul(100).reset_index()
        counts.columns = [category_col, 'percentage']

    else:
        counts = data.groupby([category_col, hue_col])[category_col].count().reset_index(name='count')
        counts['percentage'] = counts.groupby(category_col)['count'].transform(lambda x: (x / x.sum()) * 100)

    # Sort the counts by category
    counts = counts.sort_values(category_col)

    # Create the countplot
    if horizontal:
        ax = sns.barplot(x='percentage', y=category_col, hue=hue_col, data=counts, orient='h', **kwargs)
        ax.set_xlim((0,100))
    else:
        ax = sns.barplot(x=category_col, y='percentage', hue=hue_col, data=counts, **kwargs)
        ax.set_ylim((0,100))

    # Rotate the x-axis labels if needed
    plt.xticks(rotation=xticks_rotation)

    # Add percentages to the countplot
    for p in ax.patches:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy() 
        if horizontal:
            ax.annotate(f'{width:.1f}%', (width, y + height / 2),
                        ha='left', va='center', xytext=(5, 0), textcoords='offset points')
        else:
            ax.annotate(f'{height:.1f}%', (x + width / 2, height),
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points')
        


    # Set the title of the plot
    if title:
        ax.set_title(title)
    else:
        ax.set_title(f"Normalized Countplot by {category_col if category_col else ''} colored by {hue_col if hue_col else ''}")


