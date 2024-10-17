import csv


# %%
def log_internet_info(date_time : str,
                      router_ip : str | None,
                      network_name : str | None, 
                      router_connected : bool, 
                      internet_connected : bool) -> None:
    """_summary_

    Args:
        date_time (str): _description_
        router_ip (str): _description_
        network_name (str | None): _description_
        router_connected (bool): _description_
        internet_connected (bool): _description_
    """
    with open('internet_info.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date_time, router_ip, network_name, router_connected, internet_connected])

# %%
