from Classes.repocollection.repo import Repo


def get_small_sample():
    repos = []

    # Find repos whose releaseCount is 0 and delete them
    repos = Repo.objects().filter(releaseCount=0)
    repos.delete()

    # Find repos whose languageSize is 0 and delete them
    repos = Repo.objects().filter(languageSize=0)
    repos.delete()

    print(str(len(repos)))
