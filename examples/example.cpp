#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

int main() {
    std::ifstream infile("output.txt");
    std::string line, tmp0;
    std::istringstream tmp1;

    if (infile.is_open()) {
        while (std::getline(infile, line)) {
            // do something
        }
        tmp1 = std::istringstream(line);
        for (int i=0; i<6; ++i)
            tmp1 >> tmp0;
        std::cout << tmp0;  // prints 6th word in last line
        
    }
    else
        std::cerr << "Couldn't open file."
                  << std::endl;
    return 0;
}