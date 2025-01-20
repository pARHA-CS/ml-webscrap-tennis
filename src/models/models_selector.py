import logging
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import xgboost as xgb
import polars as pl

logger = logging.getLogger(__name__)

SEED = 1

MODELS = {
    'LogisticRegression': {
        'model': LogisticRegression(random_state=SEED, max_iter=10_000),
        'param_grid': {
            'C': [5, 10, 50, 100],
            'solver': ['liblinear']
        }
    },
    'DecisionTreeClassifier': {
        'model': DecisionTreeClassifier(random_state=SEED),
        'param_grid': {
            'max_depth': [None, 5, 10, 20],
            'min_samples_split': [2, 10, 20]
        }
    },
    'RandomForestClassifier': {
        'model': RandomForestClassifier(random_state=SEED, n_jobs=3),
        'param_grid': {
            'n_estimators': [400, 600, 800],
            'max_depth': [5, 10, 20],
            'max_samples': [0.8],
            'max_features': ['sqrt']
        }
    },
    'GradientBoostingClassifier': {
        'model': GradientBoostingClassifier(random_state=SEED),
        'param_grid': {
            'n_estimators': [50, 100, 150, 200],
            'learning_rate': [0.01, 0.1],
            'max_depth': [1, 2, 3],
            'subsample': [0.7, 0.8, 1.0]
        }
    },
    'XGBClassifier': {
        'model': xgb.XGBClassifier(random_state=SEED, eval_metric='logloss'),
        'param_grid': {
            'max_depth': [3, 6, 10],
            'learning_rate': [0.001, 0.01, 0.1],
            'n_estimators': [200, 400, 600]
        }
    },
    'KNeighborsClassifier': {
        'model': KNeighborsClassifier(n_jobs=3),
        'param_grid': {
            'n_neighbors': [3, 5, 7, 9],
            'weights': ['uniform', 'distance']
        }
    }
}


def train_test(df: pl.DataFrame, seed: int):
    """
    Sépare les données en ensembles d'entraînement et de test.

    Args:
        df (pl.DataFrame): DataFrame contenant les données avec une colonne "target" comme étiquette.
        seed (int): Valeur pour initialiser le générateur aléatoire afin d'assurer la reproductibilité.

    Returns:
        tuple: Contient quatre éléments :
            - X_train (np.ndarray): Données d'entraînement sans la cible.
            - X_test (np.ndarray): Données de test sans la cible.
            - y_train (np.ndarray): Étiquettes d'entraînement.
            - y_test (np.ndarray): Étiquettes de test.
    """

    X = df.drop("target").to_numpy()
    y = df.select("target").to_numpy().flatten()
    return train_test_split(X, y, test_size=0.2, random_state=seed)


def find_best_model(df: pl.DataFrame, seed: int) -> dict:
    """
    Identifie le meilleur modèle en testant plusieurs algorithmes avec recherche d'hyperparamètres.

    Args:
        df (pl.DataFrame): DataFrame contenant les données avec une colonne "target" comme étiquette.
        seed (int): Valeur pour initialiser le générateur aléatoire afin d'assurer la reproductibilité.

    Returns:
        dict: Un dictionnaire contenant :
            - 'model_name' (str): Nom du modèle avec la meilleure performance.
            - 'best_model' (object): Instance du meilleur modèle entraîné.
            - 'accuracy' (float): Score de précision obtenu sur le jeu de test.
    """

    X_train, X_test, y_train, y_test = train_test(df, seed)

    best_model = None
    best_score = 0
    best_name = None

    for name, config in MODELS.items():
        logger.info(f"Training {name}...")

        grid_search = GridSearchCV(config['model'], config['param_grid'], cv=5, scoring='accuracy', verbose=1)
        grid_search.fit(X_train, y_train)

        model = grid_search.best_estimator_
        y_pred = model.predict(X_test)
        score = accuracy_score(y_test, y_pred)

        logger.info(f"{name} accuracy: {score:.4f}")

        if score > best_score:
            best_score = score
            best_model = model
            best_name = name

    return {
        'model_name': best_name,
        'best_model': best_model,
        'accuracy': best_score
    }
