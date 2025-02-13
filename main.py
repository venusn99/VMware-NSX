def get_node_information():
    exit_condtion = False
    while not exit_condtion:
        pass
def run_on(input_option):
    print("input_option is", input_option)
    if input_option == 1:
        get_node_information('Manager')
    if input_option == 2:
        get_node_information('Edge_Node')
    if input_option == 3:
        pass


def main():
    # exitclause = False
    input_option= input("Select option from below\n" 
                        "\t 1) run only on NSX Manager\n"
                        "\t 2) run only on Edges\n"
                        "\t 3) run on NSX managers and Edges Transport Nodes\n")
    run_on(input_option)
if __name__== "__main__":
    main()