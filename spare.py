from scipy import stats
import numpy as np
import matplotlib.pyplot as plt


def number_of_spares(data,confidence):
    total_prob = float(0)
    num_of_spares = float(0)
    for i,x in np.ndenumerate(data):
        if total_prob <= confidence:
            total_prob = total_prob + x
        else:
            num_of_spares = i
            break
    return (total_prob,num_of_spares)

def main():
    mtbf = float(200000)
    failure_rate = float(1/mtbf)
    replinish_time = 90*24
    number_of_units = 1000

    rate = float(number_of_units*failure_rate*replinish_time)

    confidence_interval_95 = float(0.95)
    confidence_interval_99 = float(0.99)

    n = np.arange(0,200)
    y = stats.poisson.pmf(n,rate)

    np.set_printoptions(precision=3)

    prob,spares= number_of_spares(y,confidence_interval_99)


    print ("99% Confidence in spares is",prob, spares)


    plt.plot(n,y,'o-')
    plt.title('Poisson: $\lambda$=%f'%rate)
    plt.xlabel('No. of Parts')
    plt.ylabel('Probability of number of spares needed')
    plt.show()














if __name__ == '__main__':
    main()