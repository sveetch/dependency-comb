from packaging.version import Version

from dependency_comb.analyzer import DependenciesAnalyzer


def test_compute_lateness(settings):
    """
    Computed lateness should return a list of release versions with a higher version
    number than the target one.

    """
    cachedir = settings.fixtures_path / "api_cache"
    analyzer = DependenciesAnalyzer(cachedir=cachedir)

    versions = [
        {"number": Version("1.0.0"), "published_at": "evening"},
        {"number": Version("0.3.3"), "published_at": "noon"},
        {"number": Version("0.0.1"), "published_at": "morning"},
        {"number": Version("0.3.5"), "published_at": "afternoon"},
        {"number": Version("0.3.4"), "published_at": "afternoon"},
    ]

    informations = analyzer.compute_lateness(target="0.3.4", versions=versions)

    assert informations == [("1.0.0", "evening"), ("0.3.5", "afternoon")]
